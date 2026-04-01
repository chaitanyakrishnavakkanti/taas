import gradio as gr
import time
from audio_extraction import extract_audio
from speech_to_text import transcribe_audio
from correction_agent import correct_text
from validation_agent import validate_transcript
from mom_agent import generate_minutes_of_meeting
from tts_agent import text_to_speech_file


def process_video(video, progress=gr.Progress()):
    if video is None:
        return "Please upload a video file.", "N/A", " No video uploaded", None, gr.update(visible=False)
    
    # Step 1: Extract Audio
    progress(0.25, desc="Step 1/4: Extracting Audio...")
    audio_path = extract_audio(video)
    if not audio_path:
        return "Audio extraction failed.", "N/A", " Audio Extraction Error", None, gr.update(visible=False)
    
    # Step 2: Speech Recognition
    progress(0.5, desc="Step 2/4: Transcribing Audio...")
    time.sleep(1)
    raw_transcript = transcribe_audio(audio_path)
    
    # Step 3: Correction Agent
    progress(0.75, desc="Step 3/4: Refining Transcript...")
    time.sleep(1)
    corrected_transcript = correct_text(raw_transcript)
    
    # Step 4: Validation
    progress(1.0, desc="Step 4/4: Validating Results...")
    is_valid = validate_transcript(corrected_transcript)
    status = " Transcript Validated" if is_valid else " Validation Issues Found"
    
    tts_audio_path = text_to_speech_file(corrected_transcript)
    return raw_transcript, corrected_transcript, status, tts_audio_path, gr.update(visible=True)


def process_minutes(corrected_transcript, progress=gr.Progress()):
    progress(0.1, desc="Generating Minutes of Meeting...")
    mom, key_points, decisions, action_items = generate_minutes_of_meeting(corrected_transcript)
    progress(1.0, desc="Minutes Generated")
    return mom, key_points, decisions, action_items


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

            corrected_output = gr.Textbox(
                label="Step 2: AI-Corrected Transcript", 
                placeholder="Corrected text will appear here...",
                lines=10
            )

            tts_audio_output = gr.Audio(label="AI Spoken Audio (Corrected Transcript)", type="filepath")

    with gr.Row():
        with gr.Column(scale=1):
            mom_output = gr.Textbox(label="Minutes of Meeting", lines=10)
        with gr.Column(scale=1):
            key_points_output = gr.Textbox(label="Key Points", lines=10)
        with gr.Column(scale=1):
            decisions_output = gr.Textbox(label="Decisions", lines=10)
        with gr.Column(scale=1):
            action_items_output = gr.Textbox(label="Action Items", lines=10)

    gr.Markdown("""
    ---
    ### Multi-Agent Pipeline Workflow
    - Audio Extraction  
    - Speech-to-Text  
    - Correction Agent  
    - Validation Agent  
    """)

    submit_btn.click(
        fn=process_video,
        inputs=video_input,
        outputs=[raw_output, corrected_output, validation_status, tts_audio_output, mom_btn]
    )

    mom_btn.click(
        fn=process_minutes,
        inputs=corrected_output,
        outputs=[mom_output, key_points_output, decisions_output, action_items_output],
    )


if __name__ == "__main__":
    demo.launch(theme=gr.themes.Soft())