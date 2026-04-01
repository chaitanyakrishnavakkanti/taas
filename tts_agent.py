import asyncio
import os
import uuid


def text_to_speech_file(text, lang="en", output_dir="tts_outputs"):
    t = (text or "").strip()
    if not t:
        return None

    os.makedirs(output_dir, exist_ok=True)
    out_path = os.path.join(output_dir, f"tts_{uuid.uuid4().hex}.mp3")

    try:
        if lang in ("hi", "hi-IN"):
            return _edge_tts_to_file(t, out_path, voice="hi-IN-SwaraNeural")

        from gtts import gTTS
        tts = gTTS(text=t, lang=lang, tld="com", slow=False)
        tts.save(out_path)
        return out_path
    except Exception as e:
        print(f"TTS generation error: {e}")
        return None


def _edge_tts_to_file(text, out_path, voice):
    try:
        import edge_tts
    except Exception as e:
        print(f"TTS dependency issue: {e}")
        return None

    async def _synth():
        communicate = edge_tts.Communicate(text=text, voice=voice)
        await communicate.save(out_path)

    try:
        asyncio.run(_synth())
        return out_path
    except RuntimeError:
        try:
            loop = asyncio.new_event_loop()
            loop.run_until_complete(_synth())
            loop.close()
            return out_path
        except Exception as e:
            print(f"TTS generation error: {e}")
            return None
