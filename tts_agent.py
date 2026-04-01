import os
import uuid


def text_to_speech_file(text, output_dir="tts_outputs"):
    t = (text or "").strip()
    if not t:
        return None

    try:
        from gtts import gTTS
    except Exception as e:
        print(f"TTS dependency issue: {e}")
        return None

    os.makedirs(output_dir, exist_ok=True)
    out_path = os.path.join(output_dir, f"tts_{uuid.uuid4().hex}.mp3")

    try:
        tts = gTTS(text=t, lang="en")
        tts.save(out_path)
        return out_path
    except Exception as e:
        print(f"TTS generation error: {e}")
        return None
