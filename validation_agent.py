import json
import re
from dataclasses import dataclass, field
from typing import List

from gemini_service import generate_text


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
    verdict: str = "unavailable"
    confidence_score: int = 0
    summary: str = ""
    issues: List[str] = field(default_factory=list)
    strengths: List[str] = field(default_factory=list)
    suggested_actions: List[str] = field(default_factory=list)
    validator: str = "gemini"


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


def _basic_guardrail_issues(text):
    issues = []
    lowered = (text or "").lower()

    if any(marker in lowered for marker in ERROR_MARKERS):
        issues.append("Transcript still contains an upstream error message instead of natural conversation.")
    if len((text or "").strip()) < 20:
        issues.append("Transcript is too short to validate confidently.")
    if _non_empty_line_count(text) == 0:
        issues.append("Transcript has no non-empty lines.")
    if _has_speaker_formatting_issues(text):
        issues.append("Speaker labels are malformed.")

    alpha_chars = sum(ch.isalpha() for ch in (text or ""))
    if alpha_chars < 10:
        issues.append("Transcript does not contain enough alphabetic content.")

    return issues


def _extract_json_object(text):
    payload = (text or "").strip()
    if not payload:
        return {}

    fenced_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", payload, flags=re.DOTALL)
    if fenced_match:
        payload = fenced_match.group(1).strip()
    else:
        start = payload.find("{")
        end = payload.rfind("}")
        if start != -1 and end != -1 and end > start:
            payload = payload[start : end + 1]

    try:
        data = json.loads(payload)
        return data if isinstance(data, dict) else {}
    except json.JSONDecodeError:
        return {}


def _clean_string_list(values):
    cleaned = []
    if not isinstance(values, list):
        return cleaned

    for value in values:
        text = str(value or "").strip()
        if text:
            cleaned.append(text)
    return cleaned


def _normalize_validation_payload(payload):
    if not isinstance(payload, dict):
        return {}

    verdict = str(payload.get("verdict", "")).strip().lower()
    if verdict not in {"pass", "review", "fail"}:
        verdict = "review"

    score_raw = payload.get("confidence_score", payload.get("score", 0))
    try:
        confidence_score = max(0, min(100, int(score_raw)))
    except (TypeError, ValueError):
        confidence_score = 0

    is_valid = bool(payload.get("is_valid"))
    if verdict == "pass":
        is_valid = True
    elif verdict == "fail":
        is_valid = False

    return {
        "is_valid": is_valid,
        "verdict": verdict,
        "confidence_score": confidence_score,
        "summary": str(payload.get("summary", "")).strip(),
        "issues": _clean_string_list(payload.get("issues", [])),
        "strengths": _clean_string_list(payload.get("strengths", [])),
        "suggested_actions": _clean_string_list(payload.get("suggested_actions", [])),
    }


class FinalValidationAgent:
    def validate(self, corrected_text, domain_mode="meeting"):
        text = (corrected_text or "").strip()
        if not text:
            return ValidationResult(
                is_valid=False,
                verdict="fail",
                confidence_score=0,
                summary="Transcript is empty, so Gemini validation cannot verify it.",
                issues=["Transcript is empty."],
                suggested_actions=["Generate or paste a transcript before running validation."],
            )

        guardrail_issues = _basic_guardrail_issues(text)
        if guardrail_issues:
            return ValidationResult(
                is_valid=False,
                verdict="fail",
                confidence_score=0,
                summary="Transcript failed basic validation checks before Gemini review.",
                issues=guardrail_issues,
                suggested_actions=["Fix the transcript content, then run validation again."],
            )

        domain_guidance = {
            "meeting": "Judge it as a professional meeting transcript.",
            "lecture": "Judge it as a lecture or presentation transcript.",
            "interview": "Judge it as an interview transcript with speaker turns.",
            "discussion": "Judge it as a conversational discussion transcript.",
        }.get((domain_mode or "meeting").strip().lower(), "Judge it as a general spoken transcript.")

        prompt = f"""
Review the final transcript for quality.

Decide whether it is acceptable as a final transcript.
Focus on:
- whether it reads like a real transcript
- whether speaker labels are consistent if present
- whether there are obvious recognition mistakes, broken sentences, or hallucinated text
- whether punctuation and grammar are good enough for delivery
- {domain_guidance}

Return JSON only with this exact shape:
{{
  "is_valid": true,
  "verdict": "pass",
  "confidence_score": 0,
  "summary": "short summary",
  "issues": ["issue"],
  "strengths": ["strength"],
  "suggested_actions": ["action"]
}}

Rules:
- verdict must be one of "pass", "review", "fail"
- confidence_score must be an integer from 0 to 100
- keep summary under 30 words
- if the transcript is acceptable, set verdict to "pass"
- if there are quality concerns but it is still partly usable, set verdict to "review"
- if it is clearly not acceptable, set verdict to "fail"
- return JSON only

Transcript:
{text}
""".strip()

        try:
            response_text = generate_text(
                prompt,
                system_instruction="You are a strict transcript quality validator that responds with JSON only.",
                temperature=0.1,
                max_output_tokens=1024,
            )
            payload = _normalize_validation_payload(_extract_json_object(response_text))
        except Exception as exc:
            return ValidationResult(
                is_valid=False,
                verdict="unavailable",
                confidence_score=0,
                summary="Gemini validation could not be completed.",
                issues=[f"Gemini validation failed: {exc}"],
                suggested_actions=["Check Gemini API configuration and try validation again."],
            )

        if not payload:
            return ValidationResult(
                is_valid=False,
                verdict="review",
                confidence_score=0,
                summary="Gemini returned an unreadable validation response.",
                issues=["Could not parse Gemini validation output."],
                suggested_actions=["Run validation again and inspect backend logs if the problem continues."],
            )

        if payload["verdict"] == "pass" and payload["confidence_score"] == 0:
            payload["confidence_score"] = 80
        if payload["verdict"] == "review" and payload["confidence_score"] == 0:
            payload["confidence_score"] = 55
        if payload["verdict"] == "fail" and payload["confidence_score"] == 0:
            payload["confidence_score"] = 25

        if not payload["summary"]:
            payload["summary"] = "Gemini completed transcript validation."

        return ValidationResult(**payload)


def validate_transcript_detailed(corrected_text, domain_mode="meeting"):
    agent = FinalValidationAgent()
    return agent.validate(corrected_text, domain_mode=domain_mode)


def validate_transcript(corrected_text, domain_mode="meeting"):
    return validate_transcript_detailed(corrected_text, domain_mode=domain_mode).is_valid
