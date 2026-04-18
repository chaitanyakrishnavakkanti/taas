import re

from gemini_service import generate_text


def _normalize_simplified_text(text):
    cleaned_lines = []
    for raw_line in (text or "").splitlines():
        line = raw_line.strip()
        if not line:
            cleaned_lines.append("")
            continue
        line = re.sub(r"\s+", " ", line)
        if line.lower().startswith(("simplified version", "easy explanation", "summary:")):
            continue
        cleaned_lines.append(line)
    return "\n".join(cleaned_lines).strip()


class SimplificationAgent:
    def simplify(self, transcript, domain_mode="meeting"):
        source_text = (transcript or "").strip()
        if not source_text:
            return ""

        domain_guidance = {
            "meeting": "Explain it like a clear workplace update.",
            "lecture": "Explain it like simple study notes for a student.",
            "interview": "Explain it like an easy summary of the important answers.",
            "discussion": "Explain it like a clear conversation summary.",
        }.get((domain_mode or "meeting").strip().lower(), "Explain it in simple language.")

        prompt = f"""
Rewrite the transcript below in a simplified, easy-to-understand form.

Rules:
- Use short sentences.
- Use simple words.
- Keep the original meaning.
- Keep important decisions, action items, and warnings.
- Do not add new facts.
- If speaker labels exist, you may keep them only when they help understanding.
- Return only the simplified explanation.
- {domain_guidance}

Transcript:
{source_text}
""".strip()

        try:
            response_text = generate_text(
                prompt,
                system_instruction="You simplify transcripts into plain, easy-to-understand language.",
                temperature=0.2,
                max_output_tokens=3072,
            )
        except Exception as exc:
            print(f"Gemini simplification issue: {exc}")
            return source_text

        normalized = _normalize_simplified_text(response_text)
        return normalized if normalized else source_text


def simplify_transcript(transcript, domain_mode="meeting"):
    agent = SimplificationAgent()
    return agent.simplify(transcript, domain_mode=domain_mode)
