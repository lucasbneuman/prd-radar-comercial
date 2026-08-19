import unittest

from radar_comercial.report_orchestration import orchestrate_demo_lead_reports


class ReportOrchestrationTest(unittest.TestCase):
    def test_orchestrate_demo_lead_reports_builds_source_reports_and_consolidated_report(self):
        result = orchestrate_demo_lead_reports("lead-apex")

        self.assertEqual(result["lead_id"], "lead-apex")
        self.assertEqual(result["orchestration_backend"], "linear")
        self.assertEqual(result["source_count"], 2)
        self.assertEqual(len(result["source_reports"]), 2)
        self.assertEqual(result["consolidated_report"]["source_label"], "CRM demo · Apex Analytics")
        self.assertEqual(result["source_reports"][0]["source"]["source_type"], "Meet")
        self.assertIn("source_label", result["source_reports"][0]["report"])
        self.assertIn("priority", result["consolidated_report"])

    def test_orchestrate_demo_lead_reports_returns_none_for_unknown_lead(self):
        self.assertIsNone(orchestrate_demo_lead_reports("lead-missing"))


if __name__ == "__main__":
    unittest.main()
