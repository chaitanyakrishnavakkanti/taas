import ollama


class MinutesOfMeetingAgent:
    def __init__(self, model="gemma:2b"):
        self.model = model

    def generate_minutes(self, corrected_transcript):
        transcript = (corrected_transcript or "").strip()
        if not transcript:
            return "", "", "", ""

        prompt = f"""
You are an expert meeting assistant.

Given the meeting transcript below, produce professional Minutes of Meeting with these sections.
Return ONLY the content in this exact format:

Minutes of Meeting:
<paragraph summary>

Key Points:
- <bullet>
- <bullet>

Decisions:
- <bullet>
- <bullet>

Action Items:
- <Owner>: <Action> (Due: <date or TBD>)
- <Owner>: <Action> (Due: <date or TBD>)

Transcript:
{transcript}
"""

        try:
            response = ollama.chat(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
            )
            content = (response.get("message", {}) or {}).get("content", "")
            content = (content or "").strip()
        except Exception as e:
            print(f"Ollama connection issue: {e}")
            content = ""

        if not content:
            mom = "Minutes of Meeting:\n" + transcript[:1200]
            return mom, "", "", ""

        mom, key_points, decisions, action_items = _split_sections(content)
        return mom, key_points, decisions, action_items


def _split_sections(text):
    t = (text or "").strip()

    def extract(label):
        idx = t.lower().find(label.lower())
        return idx

    labels = [
        "Minutes of Meeting:",
        "Key Points:",
        "Decisions:",
        "Action Items:",
    ]

    positions = {lab: extract(lab) for lab in labels}
    found = [(lab, pos) for lab, pos in positions.items() if pos != -1]
    found.sort(key=lambda x: x[1])

    if not found:
        return t, "", "", ""

    sections = {"Minutes of Meeting:": "", "Key Points:": "", "Decisions:": "", "Action Items:": ""}

    for i, (lab, start) in enumerate(found):
        end = found[i + 1][1] if i + 1 < len(found) else len(t)
        chunk = t[start:end].strip()
        if chunk.lower().startswith(lab.lower()):
            chunk = chunk[len(lab):].strip()
        sections[lab] = chunk

    mom_text = "Minutes of Meeting:\n" + sections["Minutes of Meeting:"].strip()
    return (
        mom_text.strip(),
        sections["Key Points:"].strip(),
        sections["Decisions:"].strip(),
        sections["Action Items:"].strip(),
    )


def generate_minutes_of_meeting(corrected_transcript):
    agent = MinutesOfMeetingAgent()
    return agent.generate_minutes(corrected_transcript)
