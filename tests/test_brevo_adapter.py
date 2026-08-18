import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from radar_comercial.brevo_adapter import deal_to_case, list_brevo_deal_summaries


class BrevoAdapterTest(unittest.TestCase):
    def test_maps_deal_and_contact_to_case(self):
        deal = {
            "id": "deal-1",
            "attributes": {
                "deal_name": "Lucas Benites",
                "number_of_activities": 3,
                "pipeline": "pipe-1",
                "deal_stage": "stage-1",
                "lost_reason": "not_interested",
            },
            "linkedContactsIds": [46],
        }
        contact = {
            "id": 46,
            "email": "lucas@example.com",
            "attributes": {"NOMBRE": "Lucas", "APELLIDOS": "Benites"},
        }

        case = deal_to_case(deal, contact)

        self.assertEqual(case["company"], "Lucas Benites")
        self.assertEqual(case["case_type"], "outbound_warm")
        self.assertIn("3 actividades registradas en Brevo", case["signals"])
        self.assertIn("motivo de pérdida histórico: not_interested", case["risks"])

    @patch("radar_comercial.brevo_adapter._fetch_json")
    def test_lists_latest_deal_summaries(self, mock_fetch):
        mock_fetch.return_value = {
            "items": [
                {
                    "id": "deal-1",
                    "attributes": {
                        "deal_name": "Lucas Benites",
                        "number_of_activities": 3,
                        "deal_stage": "stage-1",
                    },
                }
            ]
        }

        deals = list_brevo_deal_summaries(limit=5)

        self.assertEqual(deals[0]["id"], "deal-1")
        self.assertIn("Lucas Benites", deals[0]["label"])


if __name__ == "__main__":
    unittest.main()
