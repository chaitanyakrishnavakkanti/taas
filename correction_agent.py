import ollama


class CorrectionAgent:
    """
    Grammar correction agent using Ollama
    """

    def __init__(self, model="gemma:2b"):
        self.model = model

    def correct_text(self, transcript):

        prompt = f"""
Correct grammar and spelling in the transcript below.

Rules:
- Preserve speaker labels like "Person 1:" and "Person 2:".
- Preserve line breaks.
- Return ONLY the corrected transcript text.

Transcript:
{transcript}
"""

        try:
            response = ollama.chat(
                model=self.model,
                messages=[{"role": "user", "content": prompt}]
            )

            corrected = response["message"]["content"].strip()

            unwanted_prefixes = (
                "Sure,",
                "Corrected:",
                "Correction:",
                "Sentence:",
                "Transcript:",
                "Input:",
                "Output:",
                "Important",
                "Rules:",
                "Result:",
            )

            cleaned_lines = []
            for raw_line in corrected.split("\n"):
                line = raw_line.strip()
                if not line:
                    cleaned_lines.append("")
                    continue

                line = line.lstrip("> *-").strip()
                lowered = line.lower()
                if lowered.startswith("transcript:") and ("person 1" not in lowered and "person 2" not in lowered):
                    continue

                skip = False
                for p in unwanted_prefixes:
                    if line.startswith(p):
                        remainder = line[len(p):].strip()
                        if remainder:
                            line = remainder
                        else:
                            skip = True
                        break

                if skip:
                    continue
                cleaned_lines.append(line)

            final_text = "\n".join(cleaned_lines).strip()
            return final_text if final_text else transcript
        except Exception as e:
            print(f"Ollama connection issue: {e}")
            return f"(Ollama connection failed. Returning Raw Transcript)\n\n{transcript}"


def correct_text(transcript):
    """
    Helper function used by other modules (Renamed for compatibility with app.py)
    """
    agent = CorrectionAgent()
    return agent.correct_text(transcript)


if __name__ == "__main__":

    raw_text = "helo my nme is chaitanya"

    corrected = correct_text(raw_text)

    print("\nRaw Transcript:")
    print(raw_text)

    print("\nCorrected Transcript:")
    print(corrected)
