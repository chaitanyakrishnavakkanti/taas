import ollama


def _extract_devanagari(text):
    t = text or ""
    kept = []
    for ch in t:
        o = ord(ch)
        if 0x0900 <= o <= 0x097F:
            kept.append(ch)
        elif kept and ch in (" ", "\n", "\t", ".", ",", "!", "?", "-", ":", ";", "(", ")"):
            kept.append(ch)
    cleaned = "".join(kept)
    cleaned = "\n".join([ln.strip() for ln in cleaned.splitlines() if ln.strip()])
    return cleaned.strip()


class TranslationAgent:
    def __init__(self, model="gemma:2b"):
        self.model = model

    def translate_to_hindi(self, text):
        t = (text or "").strip()
        if not t:
            return ""

        prompts = [
            f"""
Translate the text to Hindi.
Rules:
- Output must be ONLY Hindi written in Devanagari script.
- Do NOT include any English.
- Do NOT include labels, quotes, romanization, or explanations.

Text:
{t}
""".strip(),
            f"""
Return ONLY the Hindi translation in Devanagari characters (Unicode \u0900-\u097F).
If you cannot comply, return an empty string.

Text:
{t}
""".strip(),
        ]

        last = ""
        for prompt in prompts:
            try:
                response = ollama.chat(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                )
                content = (response.get("message", {}) or {}).get("content", "")
                content = (content or "").strip()
                last = content
                cleaned = _extract_devanagari(content)
                if cleaned:
                    return cleaned
            except Exception as e:
                print(f"Ollama connection issue: {e}")
                return ""

        return _extract_devanagari(last)


def translate_to_hindi(text):
    agent = TranslationAgent()
    return agent.translate_to_hindi(text)
