import unittest

from mom_agent import _split_sections
from translation_agent import _extract_devanagari
from validation_agent import validate_transcript_detailed


class HelperTests(unittest.TestCase):
    def test_extract_devanagari_keeps_hindi_text(self):
        text = 'Here you go: "नमस्ते दुनिया!" English should disappear.'
        self.assertEqual(_extract_devanagari(text), "नमस्ते दुनिया!")

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

    def test_validate_transcript_reports_issues(self):
        result = validate_transcript_detailed("validation issues")
        self.assertFalse(result.is_valid)
        self.assertTrue(result.issues)

    def test_validate_transcript_accepts_well_formed_text(self):
        transcript = "Person 1: We reviewed the roadmap.\nPerson 2: We agreed to ship next week."
        result = validate_transcript_detailed(transcript)
        self.assertTrue(result.is_valid)
        self.assertEqual(result.issues, [])


if __name__ == "__main__":
    unittest.main()
