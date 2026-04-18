from functools import lru_cache

import numpy as np
import whisper

from config import WHISPER_MODEL_SIZE
from runtime_utils import ensure_ffmpeg_in_path


@lru_cache(maxsize=2)
def _load_whisper_model(model_size):
    ensure_ffmpeg_in_path()
    print(f"Loading Whisper model: {model_size}")
    return whisper.load_model(model_size)


def _load_audio_input(audio_path, sample_rate=16000):
    """
    Load audio into memory so transcription does not depend on ffmpeg being
    discoverable from the current shell.
    """
    try:
        import librosa

        audio, _ = librosa.load(audio_path, sr=sample_rate, mono=True)
        return audio.astype(np.float32)
    except Exception:
        return audio_path


class SpeechToTextAgent:
    """
    Speech Recognition Agent using Whisper
    Converts audio files into text transcripts
    """

    def __init__(self, model_size=WHISPER_MODEL_SIZE):
        """
        Initialize Whisper speech recognition model
        """
        self.model = _load_whisper_model(model_size)

    def transcribe(self, audio_path, language=None):
        """
        Convert audio speech to text

        Parameters:
        audio_path (str): Path to audio file

        Returns:
        str: Raw transcript
        """

        print(f"Transcribing audio file: {audio_path}")

        language = None if not language or language == "auto" else language
        result = self.model.transcribe(_load_audio_input(audio_path), language=language)
        return result["text"]

    def transcribe_with_segments(self, audio_path, language=None):
        print(f"Transcribing audio file: {audio_path}")
        language = None if not language or language == "auto" else language
        result = self.model.transcribe(_load_audio_input(audio_path), language=language)
        text = result.get("text", "")
        segments = result.get("segments", [])
        return text, segments


def transcribe_audio(audio_path, language=None):
    """
    Helper function used by other modules
    """

    agent = SpeechToTextAgent()

    transcript = agent.transcribe(audio_path, language=language)

    return transcript


def transcribe_audio_with_segments(audio_path, language=None):
    agent = SpeechToTextAgent()
    text, segments = agent.transcribe_with_segments(audio_path, language=language)
    return text, segments


# Test block
if __name__ == "__main__":

    # Your audio file
    audio_file = "audio.wav"

    # Run transcription
    text = transcribe_audio(audio_file)

    print("\nRaw Transcript:")
    print(text)
