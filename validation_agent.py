import re
from dataclasses import dataclass, field
from typing import List


ERROR_MARKERS = (
    "gemini connection failed",
    "missing gemini_api_key",
    "audio extraction failed",
    "tts error",
    "validation issues",
)


@dataclass
class ValidationResult:
    is_valid: bool = False
    issues: List[str] = field(default_factory=list)


def _non_empty_line_count(text):
    return len([line for line in (text or "").splitlines() if line.strip()])


def _has_speaker_formatting_issues(text):
    speaker_lines = [
        line.strip()
        for line in (text or "").splitlines()
        if line.strip().lower().startswith("person ")
    ]
    if not speaker_lines:
        return False

    speaker_line_re = re.compile(r"^Person\s+\d+\s*:\s+\S+", flags=re.IGNORECASE)
    return any(not speaker_line_re.match(line) for line in speaker_lines)


def validate_transcript_detailed(corrected_text):
    """Perform lightweight validation checks and return actionable feedback."""
    text = (corrected_text or "").strip()
    issues = []

    if not text:
        issues.append("Transcript is empty.")
        return ValidationResult(is_valid=False, issues=issues)

    lowered = text.lower()
    if any(marker in lowered for marker in ERROR_MARKERS):
        issues.append("Transcript still contains an error marker from an upstream stage.")

    if len(text) < 20:
        issues.append("Transcript is unusually short.")

    if _non_empty_line_count(text) == 0:
        issues.append("Transcript has no non-empty lines.")

    if _has_speaker_formatting_issues(text):
        issues.append("Speaker labels are malformed.")

    alpha_chars = sum(ch.isalpha() for ch in text)
    if alpha_chars < 10:
        issues.append("Transcript does not contain enough alphabetic content.")

    return ValidationResult(is_valid=not issues, issues=issues)


def validate_transcript(corrected_text):
    return validate_transcript_detailed(corrected_text).is_valid
