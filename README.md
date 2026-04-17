# Adaptive Hybrid AI Transcription System

This project processes meeting audio/video with Whisper, validates and refines the transcript with Gemini, and delivers meeting notes, Hindi translation, and text-to-speech output through a FastAPI backend and React frontend.

## Features

- Video-to-audio extraction with `ffmpeg`
- Speech-to-text transcription with Whisper
- Basic speaker labeling for conversation-style audio
- Transcript correction with Gemini API
- Minutes of Meeting generation
- Hindi translation
- English and Hindi text-to-speech

## Setup

```bash
pip install -r requirements.txt
```

Gemini is the only LLM used by the active project. Set `GEMINI_API_KEY` in your environment before using correction, minutes, or translation features.

If you want to override that key locally, set `GEMINI_API_KEY` before running:

```bash
set GEMINI_API_KEY=your_api_key_here
```

## Run Backend

```bash
.\run_backend.ps1
```

## Run Frontend

```bash
.\run_frontend.ps1
```

## Optional Environment Variables

- `WHISPER_MODEL_SIZE` default: `base`
- `GEMINI_MODEL` default: `gemini-2.5-flash`
- `DEFAULT_SPEAKER_COUNT` default: `2`
