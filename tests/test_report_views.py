import unittest

from radar_comercial.report_orchestration import build_view_models_for_lead


class ReportViewsTest(unittest.TestCase):
    def test_build_view_models_for_lead_returns_commercial_and_executive_views(self):
        result = build_view_models_for_lead("lead-apex")

        self.assertEqual(result["lead_id"], "lead-apex")
        self.assertIn("commercial", result["views"])
        self.assertIn("executive", result["views"])

        commercial = result["views"]["commercial"]
        executive = result["views"]["executive"]

        self.assertEqual(commercial["audience"], "commercial")
        self.assertEqual(executive["audience"], "executive")
        self.assertIn("priority", commercial)
        self.assertIn("focus", commercial)
        self.assertIn("next_steps", commercial)
        self.assertIn("headline", executive)
        self.assertIn("source_overview", executive)
        self.assertIn("decision_note", executive)
        self.assertGreater(len(executive["source_overview"]), 0)

    def test_build_view_models_for_unknown_lead_returns_none(self):
        self.assertIsNone(build_view_models_for_lead("lead-missing"))


if __name__ == "__main__":
    unittest.main()
