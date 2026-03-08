import ollama


class CorrectionAgent:
    """
    Grammar correction agent using Ollama
    """

    def __init__(self, model="gemma:2b"):
        self.model = model

    def correct_text(self, transcript):

        prompt = f"""
You are a grammar correction system.

Correct spelling and grammar mistakes in the sentence below.

IMPORTANT RULES:
- Do NOT explain anything
- Do NOT add extra sentences
- Return ONLY the corrected sentence

Sentence:
{transcript}
"""

        try:
            response = ollama.chat(
                model=self.model,
                messages=[{"role": "user", "content": prompt}]
            )

            corrected = response["message"]["content"].strip()

            # Clean unwanted phrases
            corrected = corrected.replace("Corrected sentence:", "")
            corrected = corrected.replace("Corrected Transcript:", "")
            corrected = corrected.replace("Sure, here is the corrected transcript:", "")

            return corrected.strip()
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
