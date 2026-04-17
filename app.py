import gradio as gr

from config import DEFAULT_SPEAKER_COUNT, GEMINI_API_KEY, GEMINI_MODEL
from pipeline import run_transcription_pipeline


APP_CSS = """
.gradio-container {
    background:
        radial-gradient(circle at top left, rgba(244, 114, 182, 0.10) 0%, transparent 25%),
        radial-gradient(circle at top right, rgba(56, 189, 248, 0.18) 0%, transparent 28%),
        linear-gradient(180deg, #fcf7f0 0%, #f4f8fb 48%, #edf3f8 100%);
}
.app-shell {
    max-width: 1320px;
    margin: 0 auto;
    padding-bottom: 24px;
}
#hero {
    padding: 30px;
    border-radius: 30px;
    background:
        linear-gradient(135deg, rgba(13, 148, 136, 0.16), rgba(30, 64, 175, 0.09)),
        linear-gradient(150deg, #fff9f0 0%, #f7fbff 100%);
    border: 1px solid rgba(15, 23, 42, 0.08);
    box-shadow: 0 22px 60px rgba(15, 23, 42, 0.08);
    margin-bottom: 18px;
}
#hero h1 {
    margin: 0 0 10px 0;
    font-size: 2.35rem;
    letter-spacing: -0.04em;
    color: #0f172a;
}
#hero p {
    margin: 0;
    max-width: 760px;
    color: #475569;
    line-height: 1.65;
    font-size: 1rem;
}
.soft-card {
    border-radius: 26px;
    border: 1px solid rgba(15, 23, 42, 0.08);
    box-shadow: 0 18px 50px rgba(15, 23, 42, 0.06);
    background: rgba(255, 255, 255, 0.78);
    backdrop-filter: blur(10px);
}
.panel-pad {
    padding: 8px;
}
.status-pill {
    display: inline-block;
    padding: 6px 12px;
    border-radius: 999px;
    background: rgba(255, 255, 255, 0.84);
    color: #0f3d53;
    border: 1px solid rgba(14, 116, 144, 0.18);
    font-size: 0.92rem;
    margin-right: 8px;
    margin-top: 10px;
}
.metric-strip {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 12px;
    margin-top: 22px;
}
.metric-card {
    padding: 16px 18px;
    border-radius: 20px;
    background: rgba(255, 255, 255, 0.82);
    border: 1px solid rgba(15, 23, 42, 0.08);
}
.metric-card h3 {
    margin: 0 0 6px 0;
    font-size: 0.84rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #64748b;
}
.metric-card p {
    margin: 0;
    color: #0f172a;
    line-height: 1.5;
}
.section-title {
    margin: 4px 0 12px 0;
    font-size: 1.08rem;
    font-weight: 700;
    color: #0f172a;
}
.section-copy {
    margin: 0 0 14px 0;
    color: #475569;
    line-height: 1.58;
}
.status-panel {
    border-radius: 18px;
    background: linear-gradient(135deg, rgba(236, 253, 245, 0.96), rgba(239, 246, 255, 0.96));
    border: 1px solid rgba(16, 185, 129, 0.18);
    padding: 10px 14px;
}
.action-hint {
    margin-top: 12px;
    padding: 11px 13px;
    border-radius: 16px;
    background: rgba(255, 255, 255, 0.72);
    border: 1px dashed rgba(15, 23, 42, 0.14);
    color: #475569;
    line-height: 1.5;
}
.workflow-grid {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 12px;
}
.workflow-step {
    padding: 14px 16px;
    border-radius: 18px;
    background: rgba(255, 255, 255, 0.76);
    border: 1px solid rgba(15, 23, 42, 0.08);
}
.workflow-step strong {
    display: block;
    margin-bottom: 6px;
    color: #0f172a;
}
.workflow-step span {
    color: #475569;
    line-height: 1.48;
}
.workspace-card textarea,
.notes-card textarea {
    font-size: 0.95rem !important;
    line-height: 1.56 !important;
}
.gr-tabitem {
    padding-top: 10px !important;
}
.gr-button-primary {
    box-shadow: 0 12px 30px rgba(14, 116, 144, 0.18) !important;
}
@media (max-width: 900px) {
    .metric-strip,
    .workflow-grid {
        grid-template-columns: 1fr;
    }
}
"""


def _runtime_badges():
    gemini_status = "Gemini API Ready" if GEMINI_API_KEY else "Gemini API Key Missing"
    return (
        f"<span class='status-pill'>{gemini_status}</span>"
        f"<span class='status-pill'>Model: {GEMINI_MODEL}</span>"
    )


def _status_markdown(result):
    lines = []
    validation = result.validation
    if result.ok and validation.is_valid:
        lines.append("Status: Transcript validated")
    elif result.ok:
        lines.append("Status: Transcript generated with follow-up checks")
    else:
        lines.append("Status: Pipeline failed")

    if result.errors:
        lines.extend([f"- {message}" for message in result.errors])
    if validation.issues:
        lines.extend([f"- {issue}" for issue in validation.issues])

    return "\n".join(lines)


def process_video(video, speaker_count, progress=gr.Progress()):
    if video is None:
        return (
            "",
            "Status: No video uploaded",
            "",
            "",
            gr.update(visible=False),
            gr.update(visible=False),
            gr.update(visible=False),
            gr.update(visible=False),
            None,
            None,
            "",
            "",
            "",
        )

    try:
        progress(0.15, desc="Extracting audio and preparing transcription...")
        progress(0.45, desc="Transcribing and labeling speakers...")
        progress(0.8, desc="Cleaning and validating transcript...")
        result = run_transcription_pipeline(video, speaker_count)
        progress(1.0, desc="Pipeline complete")
    except Exception as e:
        return (
            "",
            f"Pipeline error: {e}",
            "",
            "",
            gr.update(visible=False),
            gr.update(visible=False),
            gr.update(visible=False),
            gr.update(visible=False),
            None,
            None,
            "",
            "",
            "",
        )

    can_run_followups = bool(result.corrected_transcript.strip())
    can_translate = bool(result.corrected_transcript.strip()) and bool(GEMINI_API_KEY)
    return (
        result.raw_transcript,
        _status_markdown(result),
        result.speaker_transcript,
        result.corrected_transcript,
        gr.update(visible=can_run_followups),
        gr.update(visible=can_run_followups),
        gr.update(visible=can_translate),
        gr.update(visible=False, interactive=False),
        None,
        None,
        "",
        "",
        "",
    )


def speak_corrected_english(corrected_transcript, progress=gr.Progress()):
    from tts_agent import text_to_speech_file

    progress(0.15, desc="Generating English audio...")
    audio_path = text_to_speech_file(corrected_transcript, lang="en")
    progress(1.0, desc="English audio ready")
    return audio_path


def do_translate_to_hindi(corrected_transcript, progress=gr.Progress()):
    from translation_agent import translate_to_hindi

    corrected_transcript = (corrected_transcript or "").strip()
    if not corrected_transcript:
        return "", gr.update(visible=False, interactive=False), "Translation skipped: no transcript to translate."

    progress(0.2, desc="Translating with Gemini...")
    hindi_text = translate_to_hindi(corrected_transcript)
    progress(1.0, desc="Hindi translation ready")
    if not hindi_text.strip():
        return "", gr.update(visible=False, interactive=False), "Translation failed. Check Gemini configuration and logs."
    return hindi_text, gr.update(visible=True, interactive=True), "Translation ready."


def speak_hindi(hindi_text, progress=gr.Progress()):
    from tts_agent import text_to_speech_file

    hindi_text = (hindi_text or "").strip()
    if not hindi_text:
        return None, "Hindi voice skipped: no Hindi text available."

    progress(0.2, desc="Generating Hindi audio...")
    audio_path = text_to_speech_file(hindi_text, lang="hi")
    progress(1.0, desc="Hindi audio ready")
    if not audio_path:
        return None, "Hindi audio generation failed. Check terminal logs for details."
    return audio_path, "Hindi audio ready."


def process_minutes(corrected_transcript, progress=gr.Progress()):
    from mom_agent import generate_minutes_of_meeting

    progress(0.2, desc="Generating meeting notes...")
    mom, key_points, _, _ = generate_minutes_of_meeting(corrected_transcript)
    progress(1.0, desc="Minutes ready")
    return mom, key_points


with gr.Blocks(title="Gemini Meeting Transcription Studio") as demo:
    gr.HTML("<div class='app-shell'>")
    gr.HTML(
        f"""
        <div id="hero">
            <h1>Adaptive Meeting Transcription Studio</h1>
            <p>Turn meeting recordings into structured transcripts, cleaner notes, translations, and voice outputs from one polished workspace built around review-first transcription.</p>
            <div>{_runtime_badges()}</div>
            <div class="metric-strip">
                <div class="metric-card">
                    <h3>Transcription</h3>
                    <p>Whisper creates the base transcript and speaker segmentation prepares the conversation view.</p>
                </div>
                <div class="metric-card">
                    <h3>Refinement</h3>
                    <p>Gemini improves readability, then validation checks help catch weak or malformed output.</p>
                </div>
                <div class="metric-card">
                    <h3>Delivery</h3>
                    <p>Generate meeting notes, Hindi translation, and voice outputs only when the transcript is ready.</p>
                </div>
            </div>
        </div>
        """
    )

    with gr.Row():
        with gr.Column(scale=1, elem_classes=["soft-card", "panel-pad"]):
            gr.HTML("<div class='section-title'>Control Panel</div>")
            gr.HTML(
                "<p class='section-copy'>Upload a meeting video, choose the expected speaker count, and run the full pipeline. Follow-up actions appear once a corrected transcript is available.</p>"
            )
            video_input = gr.Video(label="Meeting Video", interactive=True, height=260)
            speaker_count_input = gr.Slider(
                minimum=1,
                maximum=6,
                step=1,
                value=DEFAULT_SPEAKER_COUNT,
                label="Expected Speaker Count",
                info="Lower values are usually faster and more stable.",
            )
            submit_btn = gr.Button("Run Full Pipeline", variant="primary")
            validation_status = gr.Markdown(
                "Status: Waiting for input",
                elem_classes=["status-panel"],
            )
            gr.Markdown(
                "Gemini improves the correction, summary, and translation stages. "
                "Set `GEMINI_API_KEY` in your environment to enable those features."
            )
            mom_btn = gr.Button("Generate Meeting Minutes", variant="secondary", visible=False)
            gr.HTML(
                "<div class='action-hint'>Recommended flow: run the pipeline, review the corrected transcript, then generate notes, translation, or voice assets from the tabs on the right.</div>"
            )

        with gr.Column(scale=2, elem_classes=["soft-card", "panel-pad"]):
            gr.HTML("<div class='section-title'>Workspace</div>")
            gr.HTML(
                "<p class='section-copy'>Use the transcript tab for quality review, then move to translation, voice output, or meeting-note generation when the result looks right.</p>"
            )

            with gr.Tabs():
                with gr.Tab("Transcript Workspace"):
                    with gr.Row():
                        raw_output = gr.Textbox(
                            label="Raw Whisper Transcript",
                            lines=11,
                            placeholder="Raw speech-to-text output will appear here.",
                            elem_classes=["workspace-card"],
                        )
                        speaker_output = gr.Textbox(
                            label="Speaker-Labeled Transcript",
                            lines=11,
                            placeholder="Speaker-aware transcript will appear here.",
                            elem_classes=["workspace-card"],
                        )

                    corrected_output = gr.Textbox(
                        label="Final Corrected Transcript",
                        lines=15,
                        placeholder="Gemini-refined transcript will appear here.",
                        elem_classes=["workspace-card"],
                    )

                with gr.Tab("Voice + Translation"):
                    with gr.Row():
                        speak_en_btn = gr.Button("Create English Voice", visible=False)
                        translate_hi_btn = gr.Button("Translate to Hindi", visible=False)
                        speak_hi_btn = gr.Button("Create Hindi Voice", visible=False, interactive=False)

                    translation_status = gr.Markdown(
                        "Translation and Hindi voice status will appear here.",
                        elem_classes=["status-panel"],
                    )

                    with gr.Row():
                        tts_en_output = gr.Audio(label="English Audio", type="filepath")
                        tts_hi_output = gr.Audio(label="Hindi Audio", type="filepath")

                    hindi_output = gr.Textbox(
                        label="Hindi Translation",
                        lines=10,
                        placeholder="Hindi translation will appear here.",
                        elem_classes=["workspace-card"],
                    )

                with gr.Tab("Meeting Notes"):
                    with gr.Row():
                        mom_output = gr.Textbox(
                            label="Minutes of Meeting",
                            lines=14,
                            elem_classes=["notes-card"],
                        )
                        key_points_output = gr.Textbox(
                            label="Key Points",
                            lines=14,
                            elem_classes=["notes-card"],
                        )

    with gr.Accordion("How This Workspace Flows", open=False):
        gr.HTML(
            """
            <div class="workflow-grid">
                <div class="workflow-step">
                    <strong>1. Upload</strong>
                    <span>Choose a meeting recording and set the expected speaker count.</span>
                </div>
                <div class="workflow-step">
                    <strong>2. Transcribe</strong>
                    <span>Generate the raw transcript and the speaker-aware version side by side.</span>
                </div>
                <div class="workflow-step">
                    <strong>3. Refine</strong>
                    <span>Use Gemini cleanup plus validation feedback to get a cleaner final transcript.</span>
                </div>
                <div class="workflow-step">
                    <strong>4. Deliver</strong>
                    <span>Create notes, translation, and voice outputs from the final reviewed transcript.</span>
                </div>
            </div>
            """
        )

    gr.HTML("</div>")

    submit_btn.click(
        fn=process_video,
        inputs=[video_input, speaker_count_input],
        outputs=[
            raw_output,
            validation_status,
            speaker_output,
            corrected_output,
            mom_btn,
            speak_en_btn,
            translate_hi_btn,
            speak_hi_btn,
            tts_hi_output,
            tts_en_output,
            mom_output,
            key_points_output,
            translation_status,
        ],
    )

    speak_en_btn.click(
        fn=speak_corrected_english,
        inputs=corrected_output,
        outputs=tts_en_output,
    )

    translate_hi_btn.click(
        fn=do_translate_to_hindi,
        inputs=corrected_output,
        outputs=[hindi_output, speak_hi_btn, translation_status],
    )

    speak_hi_btn.click(
        fn=speak_hindi,
        inputs=hindi_output,
        outputs=[tts_hi_output, translation_status],
    )

    mom_btn.click(
        fn=process_minutes,
        inputs=corrected_output,
        outputs=[mom_output, key_points_output],
    )


if __name__ == "__main__":
    demo.launch(
        theme=gr.themes.Soft(primary_hue="teal", secondary_hue="blue", neutral_hue="slate"),
        css=APP_CSS,
    )
