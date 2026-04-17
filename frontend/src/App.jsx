import { useEffect, useMemo, useState } from "react";

const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";
const LANGUAGE_OPTIONS = [
  { code: "hi", label: "Hindi" },
  { code: "te", label: "Telugu" },
  { code: "kn", label: "Kannada" },
  { code: "ta", label: "Tamil" },
];

const tabs = [
  { id: "transcript", label: "Transcript Workspace" },
  { id: "voice", label: "Voice + Translation" },
  { id: "notes", label: "Meeting Notes" },
];

const initialResult = {
  rawTranscript: "",
  speakerTranscript: "",
  correctedTranscript: "",
  validation: { isValid: false, issues: [] },
  errors: [],
};

function App() {
  const [geminiConfigured, setGeminiConfigured] = useState(false);
  const [speakerCount, setSpeakerCount] = useState(2);
  const [selectedTab, setSelectedTab] = useState("transcript");
  const [videoFile, setVideoFile] = useState(null);
  const [status, setStatus] = useState("Waiting for input.");
  const [selectedLanguage, setSelectedLanguage] = useState("hi");
  const [isProcessing, setIsProcessing] = useState(false);
  const [isGeneratingEnglish, setIsGeneratingEnglish] = useState(false);
  const [isTranslating, setIsTranslating] = useState(false);
  const [isGeneratingHindi, setIsGeneratingHindi] = useState(false);
  const [result, setResult] = useState(initialResult);
  const [minutes, setMinutes] = useState("");
  const [keyPoints, setKeyPoints] = useState("");
  const [translatedText, setTranslatedText] = useState("");
  const [translationStatus, setTranslationStatus] = useState("Translation and voice status will appear here.");
  const [englishAudioUrl, setEnglishAudioUrl] = useState("");
  const [targetAudioUrl, setTargetAudioUrl] = useState("");

  const hasTranscript = useMemo(
    () => Boolean(result.correctedTranscript.trim()),
    [result.correctedTranscript]
  );

  useEffect(() => {
    fetch(`${API_BASE}/api/health`)
      .then((response) => response.json())
      .then((payload) => {
        setGeminiConfigured(Boolean(payload.geminiConfigured));
      })
      .catch(() => {
        setGeminiConfigured(false);
      });
  }, []);

  async function checkResponse(response) {
    if (response.ok) {
      return response.json();
    }

    const payload = await response.json().catch(() => ({}));
    throw new Error(payload.detail || "Request failed.");
  }

  async function handleProcessSubmit(event) {
    event.preventDefault();
    if (!videoFile) {
      setStatus("Please choose a meeting recording before running the pipeline.");
      return;
    }

    const formData = new FormData();
    formData.append("file", videoFile);
    formData.append("speaker_count", String(speakerCount));

    setIsProcessing(true);
    setStatus("Running full transcription pipeline...");
    setMinutes("");
    setKeyPoints("");
    setTranslatedText("");
    setEnglishAudioUrl("");
    setTargetAudioUrl("");
    setTranslationStatus("Translation and voice status will appear here.");

    try {
      const response = await fetch(`${API_BASE}/api/process`, {
        method: "POST",
        body: formData,
      });
      const payload = await checkResponse(response);
      setResult({
        rawTranscript: payload.rawTranscript || "",
        speakerTranscript: payload.speakerTranscript || "",
        correctedTranscript: payload.correctedTranscript || "",
        validation: payload.validation || { isValid: false, issues: [] },
        errors: payload.errors || [],
      });

      if (payload.ok && payload.validation?.isValid) {
        setStatus("Transcript validated and ready for follow-up actions.");
      } else if (payload.ok) {
        setStatus("Transcript generated with review notes. Check validation issues before delivery.");
      } else {
        setStatus("Pipeline finished with errors. Review the status and try again.");
      }
    } catch (error) {
      setResult(initialResult);
      setStatus(error.message || "Pipeline request failed.");
    } finally {
      setIsProcessing(false);
    }
  }

  async function handleGenerateMinutes() {
    if (!hasTranscript) return;

    setStatus("Generating meeting notes...");
    try {
      const response = await fetch(`${API_BASE}/api/minutes`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ corrected_transcript: result.correctedTranscript }),
      });
      const payload = await checkResponse(response);
      setMinutes(payload.minutes || "");
      setKeyPoints(payload.keyPoints || "");
      setSelectedTab("notes");
      setStatus("Meeting notes are ready.");
    } catch (error) {
      setStatus(error.message || "Meeting note generation failed.");
    }
  }

  async function handleTranslateHindi() {
    if (!hasTranscript) return;

    setIsTranslating(true);
    setTranslationStatus("Translating transcript into Hindi...");
    try {
      const response = await fetch(`${API_BASE}/api/translate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          corrected_transcript: result.correctedTranscript,
          target_language: selectedLanguage,
        }),
      });
      const payload = await checkResponse(response);
      setTranslatedText(payload.translatedText || "");
      setTranslationStatus(payload.message || "Translation ready.");
      setSelectedTab("voice");
    } catch (error) {
      setTranslationStatus(error.message || "Translation failed.");
    } finally {
      setIsTranslating(false);
    }
  }

  async function handleGenerateEnglishVoice() {
    if (!hasTranscript) return;

    setIsGeneratingEnglish(true);
    setStatus("Generating English voice output...");
    try {
      const response = await fetch(`${API_BASE}/api/tts`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: result.correctedTranscript, lang: "en" }),
      });
      const payload = await checkResponse(response);
      setEnglishAudioUrl(`${API_BASE}${payload.audioUrl}`);
      setSelectedTab("voice");
      setStatus("English audio is ready.");
    } catch (error) {
      setStatus(error.message || "English voice generation failed.");
    } finally {
      setIsGeneratingEnglish(false);
    }
  }

  async function handleGenerateHindiVoice() {
    if (!translatedText.trim()) {
      setTranslationStatus("Generate translation first.");
      return;
    }

    setIsGeneratingHindi(true);
    const selectedLanguageLabel =
      LANGUAGE_OPTIONS.find((option) => option.code === selectedLanguage)?.label || "selected";
    setTranslationStatus(`Generating ${selectedLanguageLabel} voice output...`);
    try {
      const response = await fetch(`${API_BASE}/api/tts`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: translatedText, lang: selectedLanguage }),
      });
      const payload = await checkResponse(response);
      setTargetAudioUrl(`${API_BASE}${payload.audioUrl}`);
      setTranslationStatus(`${selectedLanguageLabel} audio is ready.`);
    } catch (error) {
      setTranslationStatus(error.message || "Voice generation failed.");
    } finally {
      setIsGeneratingHindi(false);
    }
  }

  const validationIssues = result.validation?.issues || [];
  const selectedLanguageLabel =
    LANGUAGE_OPTIONS.find((option) => option.code === selectedLanguage)?.label || "Selected";

  return (
    <div className="shell">
      <section className="hero">
        <div className="hero-copy">
          <span className="eyebrow">Adaptive Hybrid AI Transcription System</span>
          <h1>Build transcripts, notes, translation, and voice output from one research-grade workspace.</h1>
          <p>
            A full app experience for meeting transcription with Whisper, Gemini cleanup,
            validation feedback, meeting-note generation, Hindi translation, and TTS delivery.
          </p>
          <div className="badge-row">
            <span className="badge">Whisper + Gemini</span>
            <span className="badge">Validation Loop Ready</span>
            <span className="badge">FastAPI + React</span>
          </div>
        </div>
        <div className="hero-grid">
          <MetricCard
            label="Pipeline"
            value="Transcribe, validate, refine, summarize, translate, and voice"
          />
          <MetricCard
            label="Best For"
            value="Meetings, interviews, lectures, multi-speaker discussions"
          />
          <MetricCard
            label="Working Style"
            value="Review-first workflow with follow-up outputs only when transcript is ready"
          />
        </div>
      </section>

      <main className="workspace">
        <aside className="panel control-panel">
          <div className="section-heading">Control Panel</div>
          <p className="section-copy">
            Upload your recording, set the expected speaker count, and run the full pipeline.
            Follow-up actions unlock once a corrected transcript is available.
          </p>

          <form onSubmit={handleProcessSubmit} className="stack">
            <label className="field">
              <span>Meeting video or audio</span>
              <input
                type="file"
                accept="video/*,audio/*"
                onChange={(event) => setVideoFile(event.target.files?.[0] || null)}
              />
            </label>

            <label className="field">
              <span>Expected speaker count</span>
              <input
                type="range"
                min="1"
                max="6"
                step="1"
                value={speakerCount}
                onChange={(event) => setSpeakerCount(Number(event.target.value))}
              />
              <strong>{speakerCount}</strong>
            </label>

            <button className="primary-button" type="submit" disabled={isProcessing}>
              {isProcessing ? "Running pipeline..." : "Run Full Pipeline"}
            </button>
          </form>

          <div className="status-card">
            <strong>Pipeline status</strong>
            <p>{status}</p>
          </div>

          <div className="hint-card">
            Review the corrected transcript before generating notes, translation, or voice output.
            {!geminiConfigured
              ? " Gemini is not configured on the backend right now, so translation is disabled."
              : ""}
          </div>

          <div className="action-stack">
            <button disabled={!hasTranscript || isGeneratingEnglish} onClick={handleGenerateEnglishVoice}>
              {isGeneratingEnglish ? "Generating English voice..." : "Create English Voice"}
            </button>
            <button
              disabled={!hasTranscript || isTranslating || !geminiConfigured}
              onClick={handleTranslateHindi}
            >
              {isTranslating ? "Translating..." : `Translate to ${selectedLanguageLabel}`}
            </button>
            <button
              disabled={!translatedText.trim() || isGeneratingHindi}
              onClick={handleGenerateHindiVoice}
            >
              {isGeneratingHindi ? "Generating voice..." : `Generate ${selectedLanguageLabel} Voice`}
            </button>
            <button disabled={!hasTranscript} onClick={handleGenerateMinutes}>
              Generate Meeting Minutes
            </button>
          </div>
        </aside>

        <section className="panel main-panel">
          <div className="section-heading">Workspace</div>
          <p className="section-copy">
            Use the transcript workspace for quality review, then move to notes and delivery tabs
            when the output is ready.
          </p>

          <div className="tabs">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                className={selectedTab === tab.id ? "tab active" : "tab"}
                onClick={() => setSelectedTab(tab.id)}
              >
                {tab.label}
              </button>
            ))}
          </div>

          {selectedTab === "transcript" && (
            <div className="tab-panel">
              <div className="transcript-grid">
                <TextPanel label="Raw Whisper Transcript" value={result.rawTranscript} />
                <TextPanel label="Speaker-Labeled Transcript" value={result.speakerTranscript} />
              </div>
              <TextPanel label="Final Corrected Transcript" value={result.correctedTranscript} tall />

              <div className="review-grid">
                <div className="info-panel">
                  <strong>Validation</strong>
                  <p>{result.validation?.isValid ? "Transcript validated." : "Review recommended before delivery."}</p>
                  {validationIssues.length > 0 ? (
                    <ul>
                      {validationIssues.map((issue) => (
                        <li key={issue}>{issue}</li>
                      ))}
                    </ul>
                  ) : (
                    <p>No validation issues reported.</p>
                  )}
                </div>

                <div className="info-panel">
                  <strong>Pipeline notes</strong>
                  {result.errors.length > 0 ? (
                    <ul>
                      {result.errors.map((issue) => (
                        <li key={issue}>{issue}</li>
                      ))}
                    </ul>
                  ) : (
                    <p>No pipeline errors reported.</p>
                  )}
                </div>
              </div>
            </div>
          )}

          {selectedTab === "voice" && (
            <div className="tab-panel">
              <div className="status-card">
                <strong>Translation + voice status</strong>
                <p>{translationStatus}</p>
              </div>
              <label className="field">
                <span>Translation language</span>
                <select
                  value={selectedLanguage}
                  onChange={(event) => setSelectedLanguage(event.target.value)}
                >
                  {LANGUAGE_OPTIONS.map((option) => (
                    <option key={option.code} value={option.code}>
                      {option.label}
                    </option>
                  ))}
                </select>
              </label>
              <div className="inline-actions">
                <button
                  className="secondary-button"
                  disabled={!hasTranscript || isTranslating || !geminiConfigured}
                  onClick={handleTranslateHindi}
                >
                  {isTranslating ? "Translating..." : `Translate to ${selectedLanguageLabel}`}
                </button>
                <button
                  className="secondary-button"
                  disabled={!translatedText.trim() || isGeneratingHindi}
                  onClick={handleGenerateHindiVoice}
                >
                  {isGeneratingHindi ? "Generating..." : `Generate ${selectedLanguageLabel} Voice`}
                </button>
              </div>
              <div className="audio-grid">
                <AudioCard label="English Audio" src={englishAudioUrl} />
                <AudioCard
                  label={`${selectedLanguageLabel} Audio`}
                  src={targetAudioUrl}
                />
              </div>
              <TextPanel
                label={`${selectedLanguageLabel} Translation`}
                value={translatedText}
                tall
              />
            </div>
          )}

          {selectedTab === "notes" && (
            <div className="tab-panel notes-grid">
              <TextPanel label="Minutes of Meeting" value={minutes} tall />
              <TextPanel label="Key Points" value={keyPoints} tall />
            </div>
          )}
        </section>
      </main>
    </div>
  );
}

function MetricCard({ label, value }) {
  return (
    <article className="metric-card">
      <span>{label}</span>
      <p>{value}</p>
    </article>
  );
}

function TextPanel({ label, value, tall = false }) {
  return (
    <article className={tall ? "text-panel tall" : "text-panel"}>
      <div className="panel-label">{label}</div>
      <textarea readOnly value={value || ""} placeholder={`${label} will appear here.`} />
    </article>
  );
}

function AudioCard({ label, src }) {
  return (
    <article className="audio-card">
      <div className="panel-label">{label}</div>
      {src ? <audio controls src={src} /> : <p>Audio output will appear here.</p>}
    </article>
  );
}

export default App;
