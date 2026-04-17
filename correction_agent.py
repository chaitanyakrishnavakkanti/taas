import re

from gemini_service import generate_text


def _basic_cleanup(text):
    cleaned_lines = []
    for raw_line in (text or "").splitlines():
        line = raw_line.strip()
        if not line:
            continue
        line = re.sub(r"\s+", " ", line)
        cleaned_lines.append(line)
    return "\n".join(cleaned_lines).strip()


def _post_process(text, fallback):
    cleaned = []
    for raw_line in (text or "").splitlines():
        line = raw_line.strip().lstrip("> *-").strip()
        if not line:
            cleaned.append("")
            continue
        if line.lower().startswith(("here is", "corrected transcript", "transcript:")):
            continue
        cleaned.append(line)

    final_text = "\n".join(cleaned).strip()
    return final_text if final_text else fallback


class CorrectionAgent:
    """
    Fast transcript cleanup using Gemini.
    """

    def correct_text(self, transcript):
        cleaned_input = _basic_cleanup(transcript)
        if not cleaned_input:
            return ""

        prompt = f"""
Lightly correct the transcript below.

Rules:
- Preserve speaker labels like "Person 1:" exactly.
- Preserve line breaks.
- Fix spelling, punctuation, casing, and obvious grammar only.
- Do not summarize, explain, or rewrite the meaning.
- Return only the corrected transcript.

Transcript:
{cleaned_input}
""".strip()

        try:
            corrected = generate_text(
                prompt,
                system_instruction="You are a fast transcript cleanup assistant.",
                temperature=0.1,
                max_output_tokens=3072,
            )
            return _post_process(corrected, cleaned_input)
        except Exception as e:
            print(f"Gemini correction issue: {e}")
            return cleaned_input


def correct_text(transcript):
    agent = CorrectionAgent()
    return agent.correct_text(transcript)


if __name__ == "__main__":
    raw_text = "Person 1: helo my nme is chaitanya"
    print(correct_text(raw_text))
