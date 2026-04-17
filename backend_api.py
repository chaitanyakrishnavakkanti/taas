import mimetypes
import shutil
import uuid
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

from config import GEMINI_API_KEY, GEMINI_MODEL, TEMP_DIR, TTS_OUTPUT_DIR
from mom_agent import generate_minutes_of_meeting
from pipeline import run_transcription_pipeline
from translation_agent import LANGUAGE_SPECS, translate_text
from tts_agent import text_to_speech_file


TEMP_DIR.mkdir(exist_ok=True)
TTS_OUTPUT_DIR.mkdir(exist_ok=True)

app = FastAPI(title="Adaptive Hybrid AI Transcription System API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class TranscriptRequest(BaseModel):
    corrected_transcript: str
    target_language: str = "hi"


class TTSRequest(BaseModel):
    text: str
    lang: str = "en"


def _public_audio_url(audio_path: str) -> str:
    path = Path(audio_path)
    return f"/api/media/audio/{path.name}"


@app.get("/api/health")
def health():
    return {
        "ok": True,
        "service": "adaptive-hybrid-ai-transcription-system",
        "geminiConfigured": bool(GEMINI_API_KEY),
        "geminiModel": GEMINI_MODEL,
    }


@app.post("/api/process")
async def process(
    file: UploadFile = File(...),
    speaker_count: int = Form(2),
):
    suffix = Path(file.filename or "upload.bin").suffix or ".bin"
    upload_path = TEMP_DIR / f"upload_{uuid.uuid4().hex}{suffix}"

    with upload_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        result = run_transcription_pipeline(str(upload_path), speaker_count)
        return {
            "ok": result.ok,
            "rawTranscript": result.raw_transcript,
            "speakerTranscript": result.speaker_transcript,
            "correctedTranscript": result.corrected_transcript,
            "validation": {
                "isValid": result.validation.is_valid,
                "issues": result.validation.issues,
            },
            "errors": result.errors,
            "meta": {
                "speakerCount": speaker_count,
                "sourceFilename": file.filename,
            },
        }
    finally:
        await file.close()


@app.post("/api/translate")
def translate(payload: TranscriptRequest):
    if not GEMINI_API_KEY:
        raise HTTPException(
            status_code=503,
            detail="Gemini is not configured on the backend. Set GEMINI_API_KEY and restart the backend.",
        )

    transcript = (payload.corrected_transcript or "").strip()
    target_language = (payload.target_language or "hi").strip().lower()
    if not transcript:
        raise HTTPException(status_code=400, detail="No transcript provided for translation.")
    if target_language not in LANGUAGE_SPECS:
        raise HTTPException(status_code=400, detail="Unsupported translation language.")

    translated_text = translate_text(transcript, target_language=target_language)
    if not translated_text:
        raise HTTPException(
            status_code=502,
            detail="Translation failed. Check Gemini configuration and backend logs.",
        )

    return {
        "ok": True,
        "translatedText": translated_text,
        "targetLanguage": target_language,
        "message": "Translation ready.",
    }


@app.post("/api/minutes")
def minutes(payload: TranscriptRequest):
    transcript = (payload.corrected_transcript or "").strip()
    if not transcript:
        raise HTTPException(status_code=400, detail="No transcript provided for meeting notes.")

    mom, key_points, decisions, action_items = generate_minutes_of_meeting(transcript)
    return {
        "ok": True,
        "minutes": mom,
        "keyPoints": key_points,
        "decisions": decisions,
        "actionItems": action_items,
    }


@app.post("/api/tts")
def text_to_speech(payload: TTSRequest):
    text = (payload.text or "").strip()
    lang = (payload.lang or "en").strip() or "en"

    if not text:
        raise HTTPException(status_code=400, detail="No text provided for text-to-speech.")

    audio_path = text_to_speech_file(text, lang=lang)
    if not audio_path:
        raise HTTPException(status_code=502, detail="Text-to-speech generation failed.")

    return {
        "ok": True,
        "audioUrl": _public_audio_url(audio_path),
        "language": lang,
    }


@app.get("/api/media/audio/{filename}")
def get_audio(filename: str):
    file_path = TTS_OUTPUT_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Audio file not found.")

    media_type, _ = mimetypes.guess_type(file_path.name)
    return FileResponse(file_path, media_type=media_type or "audio/mpeg", filename=file_path.name)
