import re

from gemini_service import generate_text


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
    t = re.sub(r"\n{3,}", "\n\n", t)
    return t.strip()


def _normalize_notes_text(text):
    t = _strip_html((text or "").strip())
    t = t.replace("__", "**")
    t = t.replace("`", "")
    t = re.sub(r"^\s*\*\s+", "- ", t, flags=re.MULTILINE)
    t = re.sub(r"\n{3,}", "\n\n", t)
    return t.strip()


def _strip_speaker_prefixes(text):
    lines = []
    for ln in (text or "").splitlines():
        stripped = re.sub(r"^(Person\s*\d+\s*:\s*)", "", ln.strip(), flags=re.IGNORECASE)
        if stripped:
            lines.append(stripped)
    return "\n".join(lines).strip()


def _meaningful(text):
    t = _strip_markdown(_strip_html((text or "").strip()))
    t = t.replace("-", "").replace("*", "").strip()
    return len(t) >= 3


def _fallback_summary(transcript):
    t = (transcript or "").strip()
    if not t:
        return ""
    one_line = " ".join([line.strip() for line in t.splitlines() if line.strip()])
    return one_line[:300]


def _split_sections(text):
    t = _normalize_notes_text(text)
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

    for index, match in enumerate(matches):
        key = key_map.get((match.group(1) or "").strip().lower())
        if not key:
            continue
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(t)
        sections[key] = t[start:end].strip()

    minutes_text = "Minutes of Meeting:\n" + (sections["minutes"] or "").strip()
    return (
        _normalize_notes_text(minutes_text).strip(),
        _normalize_notes_text(sections["key_points"]).strip(),
        _normalize_notes_text(sections["decisions"]).strip(),
        _normalize_notes_text(sections["action_items"]).strip(),
    )


class MinutesOfMeetingAgent:
    def generate_minutes(self, corrected_transcript, summary_style="concise", domain_mode="meeting"):
        transcript = _strip_markdown(_strip_speaker_prefixes(_strip_html((corrected_transcript or "").strip())))
        if not transcript:
            return "", "", "", ""

        style_guidance = {
            "concise": "Keep the notes crisp and compact.",
            "detailed": "Include fuller context for each important point, while staying structured.",
            "actions_only": "Prioritize actionable next steps and concrete follow-ups over narrative detail.",
            "executive": "Use a polished executive-summary tone with high-signal takeaways only.",
        }.get((summary_style or "concise").strip().lower(), "Keep the notes concise and useful.")
        domain_guidance = {
            "meeting": "Treat the conversation as a professional meeting.",
            "lecture": "Treat the conversation as a lecture or presentation with key teaching points.",
            "interview": "Treat the conversation as an interview and preserve the most important answers.",
            "discussion": "Treat the conversation as a collaborative discussion.",
        }.get((domain_mode or "meeting").strip().lower(), "Treat the conversation as a spoken transcript.")

        prompt = f"""
Create concise professional Minutes of Meeting from the transcript below.

Focus only on the important points discussed in the meeting.
Do not include casual filler, greetings, repetition, or small talk.
If a speaker strongly stresses that something is important, urgent, must-do, or asks others to pay attention,
preserve that point and wrap the key phrase in **double asterisks** for emphasis.
{style_guidance}
{domain_guidance}

Return only this exact plain-text structure:

Minutes of Meeting:
<1 short paragraph about the most important discussion only>

Key Points:
- <important bullet only>

Decisions:
- <bullet or - None>

Action Items:
- <Owner or Team>: <Action> (Due: TBD)

Transcript:
{transcript}
""".strip()

        try:
            content = generate_text(
                prompt,
                system_instruction="You are an expert meeting notes assistant.",
                temperature=0.2,
                max_output_tokens=2048,
            )
            content = _normalize_notes_text(content)
        except Exception as e:
            print(f"Gemini minutes issue: {e}")
            content = ""

        if not content:
            minutes = "Minutes of Meeting:\n" + transcript[:1200]
            return minutes, "", "", ""

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


def generate_minutes_of_meeting(corrected_transcript, summary_style="concise", domain_mode="meeting"):
    agent = MinutesOfMeetingAgent()
    return agent.generate_minutes(
        corrected_transcript,
        summary_style=summary_style,
        domain_mode=domain_mode,
    )
