import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
TEMP_DIR = BASE_DIR / "tmp"
TTS_OUTPUT_DIR = BASE_DIR / "tts_outputs"
ENV_FILE = BASE_DIR / ".env"


def _load_env_file(env_file):
    if not env_file.exists():
        return

    for raw_line in env_file.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


_load_env_file(ENV_FILE)

WHISPER_MODEL_SIZE = os.getenv("WHISPER_MODEL_SIZE", "base")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
DEFAULT_SPEAKER_COUNT = int(os.getenv("DEFAULT_SPEAKER_COUNT", "2"))
DEFAULT_TRANSCRIPTION_LANGUAGE = os.getenv("DEFAULT_TRANSCRIPTION_LANGUAGE", "auto")
DEFAULT_DOMAIN_MODE = os.getenv("DEFAULT_DOMAIN_MODE", "meeting")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_VALIDATION_MODEL = os.getenv("OPENROUTER_VALIDATION_MODEL", "openrouter/free")
