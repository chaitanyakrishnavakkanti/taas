import whisper


class SpeechToTextAgent:
    """
    Speech Recognition Agent using Whisper
    Converts audio files into text transcripts
    """

    def __init__(self, model_size="base"):
        """
        Initialize Whisper speech recognition model
        """
        print("Loading Whisper model...")
        self.model = whisper.load_model(model_size)

    def transcribe(self, audio_path):
        """
        Convert audio speech to text

        Parameters:
        audio_path (str): Path to audio file

        Returns:
        str: Raw transcript
        """

        print(f"Transcribing audio file: {audio_path}")

        result = self.model.transcribe(audio_path)
        return result["text"]

    def transcribe_with_segments(self, audio_path):
        print(f"Transcribing audio file: {audio_path}")
        result = self.model.transcribe(audio_path)
        text = result.get("text", "")
        segments = result.get("segments", [])
        return text, segments


def transcribe_audio(audio_path):
    """
    Helper function used by other modules
    """

    agent = SpeechToTextAgent()

    transcript = agent.transcribe(audio_path)

    return transcript


def transcribe_audio_with_segments(audio_path):
    agent = SpeechToTextAgent()
    text, segments = agent.transcribe_with_segments(audio_path)
    return text, segments


# Test block
if __name__ == "__main__":

    # Your audio file
    audio_file = "audio.wav"

    # Run transcription
    text = transcribe_audio(audio_file)

    print("\nRaw Transcript:")
    print(text)
