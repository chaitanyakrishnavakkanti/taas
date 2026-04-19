import unittest

from mom_agent import _split_sections
from simplification_agent import _normalize_simplified_text
from speaker_diarization import _smooth_speaker_sequence, format_diarized_transcript
from validation_agent import (
    _extract_json_object,
    _normalize_validation_payload,
    validate_transcript_detailed,
)


class HelperTests(unittest.TestCase):
    def test_extract_json_object_reads_fenced_json(self):
        payload = """
```json
{"is_valid": true, "verdict": "pass", "confidence_score": 91}
```
""".strip()
        self.assertEqual(
            _extract_json_object(payload),
            {"is_valid": True, "verdict": "pass", "confidence_score": 91},
        )

    def test_normalize_validation_payload_coerces_values(self):
        normalized = _normalize_validation_payload(
            {
                "is_valid": False,
                "verdict": "review",
                "metric_scores": {
                    "grammar_correctness": 70,
                    "clarity_readability": 68,
                    "sentence_structure": 65,
                    "completeness": 70,
                    "noise_reduction": 60,
                },
                "summary": "Needs a quick human check.",
                "issues": ["Minor wording issue", ""],
                "strengths": ["Clear speaker flow"],
                "suggested_actions": ["Review line 3"],
                "improvement_categories": ["clarity"],
                "editor_feedback": "Improve readability while preserving the original meaning.",
            }
        )
        self.assertEqual(normalized["verdict"], "review")
        self.assertEqual(normalized["confidence_score"], 68)
        self.assertEqual(normalized["issues"], ["Minor wording issue"])
        self.assertEqual(normalized["strengths"], ["Clear speaker flow"])
        self.assertEqual(normalized["suggested_actions"], ["Review line 3"])
        self.assertEqual(normalized["improvement_categories"], ["clarity"])
        self.assertEqual(
            normalized["editor_feedback"],
            "Improve readability while preserving the original meaning.",
        )

    def test_split_sections_parses_meeting_template(self):
        content = """
Minutes of Meeting:
Project status was reviewed.

Key Points:
- Delivery moved to Friday

Decisions:
- Proceed with QA

Action Items:
- Team: Share report (Due: TBD)
""".strip()
        minutes, key_points, decisions, action_items = _split_sections(content)
        self.assertIn("Project status was reviewed.", minutes)
        self.assertEqual(key_points, "- Delivery moved to Friday")
        self.assertEqual(decisions, "- Proceed with QA")
        self.assertEqual(action_items, "- Team: Share report (Due: TBD)")

    def test_validate_transcript_reports_empty_transcript(self):
        result = validate_transcript_detailed("")
        self.assertFalse(result.is_valid)
        self.assertEqual(result.verdict, "fail")
        self.assertTrue(result.issues)

    def test_normalize_simplified_text_removes_heading_noise(self):
        text = "Simplified version:\nThis is easy.\n\nKeep this line."
        self.assertEqual(_normalize_simplified_text(text), "This is easy.\n\nKeep this line.")

    def test_smoothing_removes_short_single_segment_flip(self):
        speakers = [1, 2, 1]
        segments = [
            {"start": 0.0, "end": 2.0, "text": "Opening update"},
            {"start": 2.0, "end": 2.4, "text": "yes"},
            {"start": 2.4, "end": 4.5, "text": "continuing the same thought"},
        ]
        self.assertEqual(_smooth_speaker_sequence(speakers, segments), [1, 1, 1])

    def test_format_diarized_transcript_merges_consecutive_segments(self):
        formatted = format_diarized_transcript(
            [
                {"speaker": 1, "text": "Hello team"},
                {"speaker": 1, "text": "today we review progress"},
                {"speaker": 2, "text": "Understood"},
            ]
        )
        self.assertEqual(
            formatted,
            "Person 1: Hello team today we review progress\nPerson 2: Understood",
        )


if __name__ == "__main__":
    unittest.main()
