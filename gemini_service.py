from functools import lru_cache

from config import GEMINI_API_KEY, GEMINI_MODEL


@lru_cache(maxsize=1)
def _get_client():
    if not GEMINI_API_KEY:
        raise RuntimeError(
            "Missing GEMINI_API_KEY. Set it in your environment before using Gemini features."
        )

    try:
        from google import genai
    except Exception as exc:
        raise RuntimeError(
            "Missing google-genai package. Install requirements before using Gemini features."
        ) from exc

    return genai.Client(api_key=GEMINI_API_KEY)


def generate_text(
    prompt,
    *,
    system_instruction=None,
    temperature=0.2,
    max_output_tokens=2048,
    model=GEMINI_MODEL,
):
    client = _get_client()

    try:
        from google.genai import types
    except Exception as exc:
        raise RuntimeError(
            "google-genai is installed incorrectly. Reinstall the dependency and try again."
        ) from exc

    response = client.models.generate_content(
        model=model,
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=temperature,
            max_output_tokens=max_output_tokens,
        ),
    )

    text = getattr(response, "text", "") or ""
    return text.strip()
