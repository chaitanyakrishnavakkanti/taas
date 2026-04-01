from gtts import gTTS
import os

def text_to_speech(text, output_file="output.mp3"):
    try:
        tts = gTTS(text=text, lang='en')
        tts.save(output_file)
        return output_file
    except Exception as e:
        print("Error in TTS:", e)
        return None