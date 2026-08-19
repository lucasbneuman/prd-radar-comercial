import unittest

from radar_comercial.crm_demo import (
    list_demo_leads,
    list_demo_source_types,
    list_demo_stages,
    list_lead_sources,
    summarize_demo_dataset,
)


class CrmDemoDatasetTest(unittest.TestCase):
    def test_dataset_exposes_expected_leads_and_summary(self):
        leads = list_demo_leads()
        summary = summarize_demo_dataset()

        self.assertGreaterEqual(len(leads), 4)
        self.assertEqual(summary["lead_count"], len(leads))
        self.assertEqual(summary["source_count"], 6)
        self.assertEqual(summary["lead_ids"][0], "lead-apex")
        self.assertIn("Discovery", summary["by_stage"])
        self.assertIn("WhatsApp", summary["by_source_type"])

    def test_leads_are_sorted_by_last_activity_desc(self):
        leads = list_demo_leads()
        dates = [lead["last_activity_at"] for lead in leads]
        self.assertEqual(dates, sorted(dates, reverse=True))

    def test_each_lead_has_at_least_one_source(self):
        leads = list_demo_leads()
        for lead in leads:
            sources = list_lead_sources(lead["id"])
            self.assertGreaterEqual(len(sources), 1, lead["id"])

    def test_dataset_taxonomy_is_reusable(self):
        self.assertIn("Discovery", list_demo_stages())
        self.assertIn("Meet", list_demo_source_types())
        self.assertIn("WhatsApp", list_demo_source_types())
        self.assertIn("Manual", list_demo_source_types())


if __name__ == "__main__":
    unittest.main()
