import ollama
import re


def _strip_html(text):
    t = text or ""
    t = re.sub(r"</?p[^>]*>", "\n", t, flags=re.IGNORECASE)
    t = re.sub(r"<br\s*/?>", "\n", t, flags=re.IGNORECASE)
    t = re.sub(r"<[^>]+>", "", t)
    t = re.sub(r"\n{3,}", "\n\n", t)
    return t.strip()


def _strip_markdown(text):
    t = text or ""
    t = t.replace("**", "")
    t = t.replace("__", "")
    t = t.replace("`", "")
    t = re.sub(r"^\s*\*\s+", "- ", t, flags=re.MULTILINE)
    t = re.sub(r"^\s*•\s+", "- ", t, flags=re.MULTILINE)
    t = re.sub(r"\n{3,}", "\n\n", t)
    return t.strip()


def _strip_speaker_prefixes(text):
    lines = []
    for ln in (text or "").splitlines():
        l = ln.strip()
        l = re.sub(r"^(Person\s*\d+\s*:\s*)", "", l, flags=re.IGNORECASE)
        if l:
            lines.append(l)
    return "\n".join(lines).strip()


class MinutesOfMeetingAgent:
    def __init__(self, model="gemma:2b"):
        self.model = model

    def generate_minutes(self, corrected_transcript):
        transcript = _strip_markdown(_strip_speaker_prefixes(_strip_html((corrected_transcript or "").strip())))
        if not transcript:
            return "", "", "", ""

        prompt = f"""
You are an expert meeting assistant.

Task: Create professional Minutes of Meeting from the transcript.

Rules:
- Output plain text only (NO HTML like <p>, NO markdown).
- Use the exact headings below.
- Use '-' bullets.
- If there are no decisions, write: - None
- If there are no action items, write: - None

Return ONLY this format:

Minutes of Meeting:
<1 short paragraph>

Key Points:
- <bullet>

Decisions:
- <bullet>

Action Items:
- <Owner or Team>: <Action> (Due: TBD)

Transcript:
{transcript}
""".strip()

        try:
            response = ollama.chat(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
            )
            content = (response.get("message", {}) or {}).get("content", "")
            content = _strip_markdown(_strip_html((content or "").strip()))
        except Exception as e:
            print(f"Ollama connection issue: {e}")
            content = ""

        if not content:
            mom = "Minutes of Meeting:\n" + transcript[:1200]
            return mom, "", "", ""

        mom, key_points, decisions, action_items = _split_sections(content)

        if not _meaningful(mom):
            mom = "Minutes of Meeting:\n" + _fallback_summary(transcript)
        if not _meaningful(key_points):
            key_points = "- None"
        if not _meaningful(decisions):
            decisions = "- None"
        if not _meaningful(action_items):
            action_items = "- None"

        return mom, key_points, decisions, action_items


def _meaningful(text):
    t = _strip_markdown(_strip_html((text or "").strip()))
    t = t.replace("-", "").replace("*", "").strip()
    return len(t) >= 3


def _fallback_summary(transcript):
    t = (transcript or "").strip()
    if not t:
        return ""
    one_line = " ".join([ln.strip() for ln in t.splitlines() if ln.strip()])
    return one_line[:300]


def _split_sections(text):
    t = _strip_markdown(_strip_html((text or "").strip()))

    heading_re = re.compile(
        r"^\s*(Minutes of Meeting|Key Points|Decisions|Action Items)\s*:?\s*$",
        flags=re.IGNORECASE | re.MULTILINE,
    )

    matches = list(heading_re.finditer(t))
    if not matches:
        return t, "", "", ""

    sections = {"minutes": "", "key_points": "", "decisions": "", "action_items": ""}
    key_map = {
        "minutes of meeting": "minutes",
        "key points": "key_points",
        "decisions": "decisions",
        "action items": "action_items",
    }

    for i, m in enumerate(matches):
        label = (m.group(1) or "").strip().lower()
        key = key_map.get(label)
        if not key:
            continue
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(t)
        chunk = t[start:end].strip()
        sections[key] = chunk

    mom_text = "Minutes of Meeting:\n" + (sections["minutes"] or "").strip()
    return (
        _strip_markdown(_strip_html(mom_text)).strip(),
        _strip_markdown(_strip_html(sections["key_points"])).strip(),
        _strip_markdown(_strip_html(sections["decisions"])).strip(),
        _strip_markdown(_strip_html(sections["action_items"])).strip(),
    )


def generate_minutes_of_meeting(corrected_transcript):
    agent = MinutesOfMeetingAgent()
    return agent.generate_minutes(corrected_transcript)
