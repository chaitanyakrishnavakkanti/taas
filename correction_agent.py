import ollama


class CorrectionAgent:
    """
    Grammar correction agent using Ollama
    """

    def __init__(self, model="gemma:2b"):
        self.model = model

    def correct_text(self, transcript):

        prompt = f"""
Correct grammar/spelling. Return ONLY the result. 
Sentence: {transcript}
Correction:"""

        try:
            response = ollama.chat(
                model=self.model,
                messages=[{"role": "user", "content": prompt}]
            )

            corrected = response["message"]["content"].strip()

            # If the model repeats the prompt, the actual answer is usually at the bottom
            # We look for common patterns or just take the last meaningful line
            lines = [l.strip() for l in corrected.split("\n") if l.strip()]
            
            # Simple list of words/patterns that indicate meta-talk or prompt repetition
            unwanted_prefixes = (
                "Sure,", "Corrected:", "Correction:", "Sentence:", 
                "Input:", "Output:", "Important", "Rules:", "Result:", "Correction:"
            )
            
            final_text = ""
            for line in reversed(lines):
                clean_line = line.lstrip("> *-").strip()
                
                # If the line starts with an unwanted prefix, strip it and see if anything remains
                found_prefix = False
                for p in unwanted_prefixes:
                    if clean_line.startswith(p):
                        clean_line = clean_line[len(p):].strip()
                        found_prefix = True
                
                # After stripping potential prefixes, if we have a solid sentence, use it
                if clean_line and len(clean_line.split()) > 2:
                    final_text = clean_line
                    break
            
            # Fallback to the last line's cleaned version if no multi-word sentence found
            if not final_text and lines:
                final_text = lines[-1].lstrip("> *-").strip()
                for p in unwanted_prefixes:
                    if final_text.startswith(p):
                        final_text = final_text[len(p):].strip()

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
