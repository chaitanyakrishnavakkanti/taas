from dataclasses import dataclass, field
from typing import List, Optional

from audio_extraction import extract_audio
from correction_agent import correct_text
from speaker_diarization import diarize_segments, format_diarized_transcript
from speech_to_text import transcribe_audio_with_segments
from validation_agent import ValidationResult, validate_transcript_detailed


@dataclass
class StageResult:
    ok: bool
    data: Optional[str] = None
    error: str = ""


@dataclass
class PipelineResult:
    ok: bool
    raw_transcript: str = ""
    speaker_transcript: str = ""
    corrected_transcript: str = ""
    validation: ValidationResult = field(default_factory=ValidationResult)
    errors: List[str] = field(default_factory=list)
    audio_path: str = ""


def run_transcription_pipeline(video_path, speaker_count) -> PipelineResult:
    if not video_path:
        return PipelineResult(ok=False, errors=["Please upload a video file."])

    audio_stage = _extract_audio_stage(video_path)
    if not audio_stage.ok:
        return PipelineResult(ok=False, errors=[audio_stage.error])

    transcription_stage = _transcription_stage(audio_stage.data)
    if not transcription_stage.ok:
        return PipelineResult(
            ok=False,
            audio_path=audio_stage.data or "",
            errors=[transcription_stage.error],
        )

    raw_transcript, segments = transcription_stage.data
    diarization_stage = _diarization_stage(audio_stage.data, segments, speaker_count)
    corrected_stage = _correction_stage(
        diarization_stage.data if diarization_stage.data else raw_transcript
    )

    validation = validate_transcript_detailed(corrected_stage.data)
    errors = []
    if not diarization_stage.ok and diarization_stage.error:
        errors.append(diarization_stage.error)
    if not corrected_stage.ok and corrected_stage.error:
        errors.append(corrected_stage.error)

    return PipelineResult(
        ok=bool(raw_transcript and corrected_stage.data),
        raw_transcript=raw_transcript,
        speaker_transcript=diarization_stage.data or "",
        corrected_transcript=corrected_stage.data or "",
        validation=validation,
        errors=errors,
        audio_path=audio_stage.data or "",
    )


def _extract_audio_stage(video_path) -> StageResult:
    audio_path = extract_audio(video_path)
    if not audio_path:
        return StageResult(ok=False, error="Audio extraction failed.")
    return StageResult(ok=True, data=audio_path)


def _transcription_stage(audio_path) -> StageResult:
    try:
        raw_transcript, segments = transcribe_audio_with_segments(audio_path)
    except Exception as exc:
        return StageResult(ok=False, error=f"Transcription failed: {exc}")

    if not raw_transcript.strip():
        return StageResult(ok=False, error="Transcription produced no text.")
    return StageResult(ok=True, data=(raw_transcript, segments))


def _diarization_stage(audio_path, segments, speaker_count) -> StageResult:
    try:
        speaker_segments = diarize_segments(audio_path, segments, n_speakers=int(speaker_count))
        speaker_transcript = format_diarized_transcript(speaker_segments)
        return StageResult(ok=True, data=speaker_transcript)
    except Exception as exc:
        return StageResult(ok=False, data="", error=f"Speaker diarization issue: {exc}")


def _correction_stage(transcript) -> StageResult:
    try:
        corrected = correct_text(transcript)
    except Exception as exc:
        return StageResult(ok=False, data=transcript, error=f"Transcript cleanup failed: {exc}")

    if not corrected.strip():
        return StageResult(
            ok=False,
            data=transcript,
            error="Transcript cleanup returned empty output; using the uncorrected transcript.",
        )
    return StageResult(ok=True, data=corrected)
