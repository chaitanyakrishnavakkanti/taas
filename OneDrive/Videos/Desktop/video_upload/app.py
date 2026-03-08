import gradio as gr
import time
from audio_extraction import extract_audio
from speech_to_text import transcribe_audio
from correction_agent import correct_text
from validation_agent import validate_transcript

def process_video(video, progress=gr.Progress()):
    """
    Main pipeline function to process the uploaded video with progress tracking.
    """
    if video is None:
        return "Please upload a video file.", "N/A", "❌ No video uploaded"
    
    # Step 1: Extract Audio
    progress(0.1, desc="Step 1/4: Extracting Audio...")
    audio_path = extract_audio(video)
    if not audio_path:
        return "Audio extraction failed.", "N/A", "❌ Audio Extraction Error (Check FFmpeg)"
    
    # Step 2: Speech Recognition
    progress(0.4, desc="Step 2/4: Transcribing Audio...")
    time.sleep(1) # Simulated delay for demo
    raw_transcript = transcribe_audio(audio_path)
    
    # Step 3: Correction Agent
    progress(0.7, desc="Step 3/4: Refining Transcript...")
    time.sleep(1) # Simulated delay for demo
    corrected_transcript = correct_text(raw_transcript)
    
    # Step 4: Validation
    progress(0.9, desc="Step 4/4: Validating Results...")
    is_valid = validate_transcript(corrected_transcript)
    status = "✅ Transcript Validated" if is_valid else "⚠️ Validation Issues Found"
    
    progress(1.0, desc="Pipeline Complete!")
    return raw_transcript, corrected_transcript, status

# Gradio UI Construction
with gr.Blocks(title="Multi-Agent Video Transcription") as demo:
    gr.Markdown(
        """
        # 🎤 Multi-Agent Video Transcription System
        *A professional tool for automated video-to-text conversion with AI-driven corrections.*
        
        ---
        """
    )
    
    with gr.Row():
        with gr.Column(scale=1, variant="panel"):
            gr.Markdown("### 📤 Input")
            video_input = gr.Video(label="Upload Video File", interactive=True)
            submit_btn = gr.Button("🚀 Generate Transcript", variant="primary")
            validation_status = gr.Markdown("Status: *Waiting for upload...*")
            
        with gr.Column(scale=2):
            gr.Markdown("### 📄 Outputs")
            raw_output = gr.Textbox(
                label="Step 1: Raw Machine Transcript", 
                placeholder="Raw text will appear here...",
                lines=5
            )
            corrected_output = gr.Textbox(
                label="Step 2: AI-Corrected Transcript", 
                placeholder="Corrected text will appear here...",
                lines=10
            )

    gr.Markdown(
        """
        ---
        ### 🛠 Multi-Agent Pipeline Workflow
        The system utilizes a specialized pipeline where agents handle different stages of the process:
        - **Audio Extraction**: Optimized for speech recognition frequencies.
        - **Speech-to-Text**: High-accuracy acoustic modeling.
        - **Correction Agent**: GPT-powered grammar and context correction.
        - **Validation Agent**: Logical checking and formatting validation.
        """
    )

    # Define interaction
    submit_btn.click(
        fn=process_video,
        inputs=video_input,
        outputs=[raw_output, corrected_output, validation_status]
    )

if __name__ == "__main__":
    demo.launch(theme=gr.themes.Soft())
