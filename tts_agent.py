import asyncio
import os
import uuid


def text_to_speech_file(text, lang="en", output_dir="tts_outputs"):
    t = (text or "").strip()
    if not t:
        return None

    os.makedirs(output_dir, exist_ok=True)
    out_path = os.path.join(output_dir, f"tts_{uuid.uuid4().hex}.mp3")

    if lang in ("hi", "hi-IN"):
        edge_path = _edge_tts_to_file(t, out_path, voice="hi-IN-SwaraNeural")
        if _is_valid_audio_file(edge_path):
            return edge_path

    try:
        from gtts import gTTS
        gtts_lang = "hi" if lang == "hi-IN" else lang
        tld = "co.in" if gtts_lang == "hi" else "com"
        tts = gTTS(text=t, lang=gtts_lang, tld=tld, slow=False)
        tts.save(out_path)
        return out_path if _is_valid_audio_file(out_path) else None
    except Exception as e:
        print(f"TTS generation error: {e}")
        return None


def _is_valid_audio_file(path):
    if not path:
        return False
    try:
        return os.path.exists(path) and os.path.getsize(path) > 0
    except Exception:
        return False


def _edge_tts_to_file(text, out_path, voice, timeout_s=45):
    try:
        import edge_tts
    except Exception as e:
        print(f"TTS dependency issue: {e}")
        return None

    async def _synth():
        communicate = edge_tts.Communicate(text=text, voice=voice)
        await asyncio.wait_for(communicate.save(out_path), timeout=timeout_s)

    try:
        asyncio.run(_synth())
        return out_path if _is_valid_audio_file(out_path) else None
    except RuntimeError:
        try:
            loop = asyncio.new_event_loop()
            loop.run_until_complete(_synth())
            loop.close()
            return out_path if _is_valid_audio_file(out_path) else None
        except Exception as e:
            print(f"TTS generation error: {e}")
            return None
    except Exception as e:
        print(f"TTS generation error: {e}")
        return None
