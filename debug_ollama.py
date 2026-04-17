from gemini_service import generate_text


def test_correction():
    transcript = (
        "Person 1: have been rolled back resources for sustainable development "
        "are severly challenged and many countries really struggle to make ends meet."
    )

    prompt = f"""
Correct spelling and grammar mistakes in the transcript below.

Rules:
- Keep the speaker label exactly as written.
- Return only the corrected transcript.

Transcript:
{transcript}
""".strip()

    print("--- PROMPT ---")
    print(prompt)

    response_text = generate_text(
        prompt,
        system_instruction="You are a transcript correction assistant.",
        temperature=0.1,
        max_output_tokens=512,
    )

    print("\n--- GEMINI RESPONSE ---")
    print(response_text)


if __name__ == "__main__":
    print("Running Gemini correction smoke test...")
    test_correction()
