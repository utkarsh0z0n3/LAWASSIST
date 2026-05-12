import unittest

from drafting.bail_template import (
    REQUIRED_MARKERS_EN,
    REQUIRED_MARKERS_HI,
    build_bail_draft,
    render_bail_en,
    validate_bail_draft,
)
from drafting.schemas import BailDraftInput


class TestBailTemplate(unittest.TestCase):
    def sample(self, **kwargs):
        base = dict(
            client_name="Test Applicant",
            court="Chief Judicial Magistrate, New Delhi",
            offence="cheating",
            facts="The prosecution alleges misrepresentation regarding a commercial transaction.",
            language="en",
            in_judicial_custody=True,
        )
        base.update(kwargs)
        return BailDraftInput(**base)

    def test_english_markers_and_name(self):
        data = self.sample(language="en")
        text, lang = build_bail_draft(data)
        self.assertEqual(lang, "en")
        for m in REQUIRED_MARKERS_EN:
            self.assertIn(m, text)
        self.assertIn(data.client_name, text)
        self.assertIn("judicial custody", text.lower())
        issues = validate_bail_draft(text, "en", expect_judicial_custody=True)
        self.assertEqual(issues, [])

    def test_hindi_markers_and_custody(self):
        data = self.sample(language="hi")
        text, lang = build_bail_draft(data)
        self.assertEqual(lang, "hi")
        for m in REQUIRED_MARKERS_HI:
            self.assertIn(m, text)
        self.assertIn("न्यायिक हिरासत", text)
        issues = validate_bail_draft(text, "hi", expect_judicial_custody=True)
        self.assertEqual(issues, [])

    def test_braces_in_facts_do_not_break_render(self):
        facts = "Section 420 {IPC} style note (see document) [exhibit A]"
        data = self.sample(facts=facts, language="en")
        text, _ = build_bail_draft(data)
        self.assertIn("{IPC}", text)
        self.assertIn("[exhibit A]", text)

    def test_empty_offence_omits_clause(self):
        data = self.sample(offence="", language="en")
        text = render_bail_en(data)
        self.assertNotIn("The applicant is accused of .", text)

    def test_no_custody_skips_custody_sentence(self):
        data = self.sample(language="en", in_judicial_custody=False)
        text = render_bail_en(data)
        self.assertNotIn("judicial custody", text.lower())
        issues = validate_bail_draft(text, "en", expect_judicial_custody=False)
        self.assertNotIn("Missing judicial custody (English)", issues)

    def test_auto_language_hindi_facts(self):
        data = self.sample(
            language="auto",
            facts="अभियुक्त को गिरफ्तार किया गया",
            offence="",
        )
        _, lang = build_bail_draft(data)
        # Without langdetect may default to en; with langdetect expect hi
        self.assertIn(lang, ("en", "hi"))


if __name__ == "__main__":
    unittest.main()
