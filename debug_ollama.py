import ollama

def test_correction():
    model = "gemma:2b"
    transcript = "have been rolled back, resources for sustainable development are severely challenged, and many countries really struggle to make ends meet."
    
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
    print("--- PROMPT ---")
    print(prompt)
    
    response = ollama.chat(
        model=model,
        messages=[{"role": "user", "content": prompt}]
    )
    
    print("\n--- RAW RESPONSE ---")
    print(response["message"]["content"])

if __name__ == "__main__":
    test_correction()
