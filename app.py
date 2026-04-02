import gradio as gr
import time
from audio_extraction import extract_audio
from speech_to_text import transcribe_audio_with_segments
from correction_agent import correct_text
from validation_agent import validate_transcript
from mom_agent import generate_minutes_of_meeting
from tts_agent import text_to_speech_file
from translation_agent import translate_to_hindi
from speaker_diarization import diarize_segments, format_diarized_transcript


def process_video(video, progress=gr.Progress()):
    if video is None:
        return (
            "Please upload a video file.",
            " No video uploaded",
            "",
            "N/A",
            gr.update(visible=False),
            gr.update(visible=False),
            gr.update(visible=False),
            "",
            gr.update(visible=False),
            None,
            None,
            "",
            "",
        )
    
    # Step 1: Extract Audio
    progress(0.25, desc="Step 1/4: Extracting Audio...")
    audio_path = extract_audio(video)
    if not audio_path:
        return (
            "Audio extraction failed.",
            " Audio Extraction Error",
            "",
            "N/A",
            gr.update(visible=False),
            gr.update(visible=False),
            gr.update(visible=False),
            "",
            gr.update(visible=False),
            None,
            None,
            "",
            "",
        )
    
    # Step 2: Speech Recognition
    progress(0.5, desc="Step 2/4: Transcribing Audio...")
    time.sleep(1)
    raw_transcript, segments = transcribe_audio_with_segments(audio_path)
    segments_with_speakers = diarize_segments(audio_path, segments, n_speakers=2)
    speaker_labeled_transcript = format_diarized_transcript(segments_with_speakers)
    
    # Step 3: Correction Agent
    progress(0.75, desc="Step 3/4: Refining Transcript...")
    time.sleep(1)
    corrected_transcript = correct_text(speaker_labeled_transcript if speaker_labeled_transcript else raw_transcript)
    
    # Step 4: Validation
    progress(1.0, desc="Step 4/4: Validating Results...")
    is_valid = validate_transcript(corrected_transcript)
    status = " Transcript Validated" if is_valid else " Validation Issues Found"

    return (
        raw_transcript,
        status,
        speaker_labeled_transcript,
        corrected_transcript,
        gr.update(visible=True),
        gr.update(visible=True),
        gr.update(visible=True),
        "",
        gr.update(visible=True, interactive=False),
        None,
        None,
        "",
        "",
    )


def speak_corrected_english(corrected_transcript, progress=gr.Progress()):
    progress(0.1, desc="Generating English speech...")
    audio_path = text_to_speech_file(corrected_transcript, lang="en")
    progress(1.0, desc="Speech ready")
    return audio_path


def do_translate_to_hindi(corrected_transcript, progress=gr.Progress()):
    progress(0.1, desc="Translating to Hindi...")
    hi = translate_to_hindi(corrected_transcript)
    progress(1.0, desc="Translation ready")
    return hi, gr.update(visible=True, interactive=True)


def speak_hindi(hindi_text, progress=gr.Progress()):
    progress(0.1, desc="Generating Hindi speech...")
    audio_path = text_to_speech_file(hindi_text, lang="hi")
    progress(1.0, desc="Speech ready")
    if not audio_path:
        msg = (hindi_text or "").strip()
        if msg:
            msg = msg + "\n\n[TTS Error: Hindi audio generation failed. Check terminal logs for dependency/network errors.]"
        else:
            msg = "[TTS Error: No Hindi text to speak.]"
        return None, msg
    return audio_path, hindi_text


def process_minutes(corrected_transcript, progress=gr.Progress()):
    progress(0.1, desc="Generating Minutes of Meeting...")
    mom, key_points, _, _ = generate_minutes_of_meeting(corrected_transcript)
    progress(1.0, desc="Minutes Generated")
    return mom, key_points


# Gradio UI
with gr.Blocks(title="Multi-Agent Video Transcription") as demo:
    gr.Markdown("""
    # Multi-Agent Video Transcription System
    *A professional tool for automated video-to-text conversion with AI-driven corrections.*
    ---
    """)

    with gr.Row():
        with gr.Column(scale=1, variant="panel"):
            gr.Markdown("### Input")
            video_input = gr.Video(label="Upload Video File", interactive=True)
            submit_btn = gr.Button(" Generate Transcript", variant="primary")
            validation_status = gr.Markdown("Status: *Waiting for upload...*")
            mom_btn = gr.Button(" Generate Minutes of Meeting", variant="secondary", visible=False)
            
        with gr.Column(scale=2):
            gr.Markdown("### Outputs")
            raw_output = gr.Textbox(
                label="Step 1: Raw Machine Transcript", 
                lines=5
            )

            speaker_output = gr.Textbox(
                label="Step 2: Speaker-Labeled Transcript (Person 1/Person 2)",
                lines=8,
            )

            corrected_output = gr.Textbox(
                label="Step 3: AI-Corrected Transcript (Speaker-Labeled)", 
                placeholder="Corrected text will appear here...",
                lines=10
            )

            speak_en_btn = gr.Button(" Speak Corrected (English)", visible=False)
            tts_en_output = gr.Audio(label="AI Spoken Audio (English)", type="filepath")

            translate_hi_btn = gr.Button(" Translate to Hindi", visible=False)
            hindi_output = gr.Textbox(label="Hindi Translation", lines=6)
            speak_hi_btn = gr.Button(" Speak Corrected (Hindi)", visible=False, interactive=False)
            tts_hi_output = gr.Audio(label="AI Spoken Audio (Hindi)", type="filepath")

    with gr.Row():
        with gr.Column(scale=1):
            mom_output = gr.Textbox(label="Minutes of Meeting", lines=10)
        with gr.Column(scale=1):
            key_points_output = gr.Textbox(label="Key Points", lines=10)

    gr.Markdown("""
    ---
    ### Multi-Agent Pipeline Workflow
    - Audio Extraction  
    - Speech-to-Text  
    - Speaker Diarization  
    - Correction Agent  
    - Validation Agent  
    """)

    submit_btn.click(
        fn=process_video,
        inputs=video_input,
        outputs=[
            raw_output,
            validation_status,
            speaker_output,
            corrected_output,
            mom_btn,
            speak_en_btn,
            translate_hi_btn,
            hindi_output,
            speak_hi_btn,
            tts_hi_output,
            tts_en_output,
            mom_output,
            key_points_output,
        ]
    )

    speak_en_btn.click(
        fn=speak_corrected_english,
        inputs=corrected_output,
        outputs=tts_en_output,
    )

    translate_hi_btn.click(
        fn=do_translate_to_hindi,
        inputs=corrected_output,
        outputs=[hindi_output, speak_hi_btn],
    )

    speak_hi_btn.click(
        fn=speak_hindi,
        inputs=hindi_output,
        outputs=[tts_hi_output, hindi_output],
    )

    mom_btn.click(
        fn=process_minutes,
        inputs=corrected_output,
        outputs=[mom_output, key_points_output],
    )


if __name__ == "__main__":
    demo.launch(theme=gr.themes.Base())