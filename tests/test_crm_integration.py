import io
import unittest
from unittest.mock import patch
from wsgiref.util import setup_testing_defaults

from radar_comercial.web import app


class CrmIntegrationWebTest(unittest.TestCase):
    def run_app(self, method="GET", body="", query_string=""):
        environ = {}
        setup_testing_defaults(environ)
        environ["REQUEST_METHOD"] = method
        environ["QUERY_STRING"] = query_string
        payload = body.encode("utf-8")
        environ["CONTENT_LENGTH"] = str(len(payload))
        environ["wsgi.input"] = io.BytesIO(payload)

        captured = {}

        def start_response(status, headers):
            captured["status"] = status
            captured["headers"] = headers

        response = b"".join(app(environ, start_response)).decode("utf-8")
        return captured["status"], dict(captured["headers"]), response

    @patch("radar_comercial.web.list_brevo_deal_summaries")
    def test_get_renders_brevo_import_section(self, mock_deals):
        mock_deals.return_value = [
            {
                "id": "deal-1",
                "label": "Lucas Benites · actividades: 1",
                "stage": "stage-1",
            }
        ]

        status, headers, response = self.run_app()

        self.assertEqual(status, "200 OK")
        self.assertEqual(headers["Content-Type"], "text/html; charset=utf-8")
        self.assertIn("Cargar desde Brevo", response)
        self.assertIn("deal-1", response)
        self.assertIn("Lucas Benites", response)

    @patch("radar_comercial.web.load_brevo_case")
    @patch("radar_comercial.web.list_brevo_deal_summaries")
    def test_get_can_load_case_from_brevo_deal(self, mock_deals, mock_case):
        mock_deals.return_value = []
        mock_case.return_value = {
            "company": "Lucas Benites",
            "objective": "ordenar seguimiento comercial",
            "pain_points": ["seguimiento manual"],
            "signals": ["1 actividad en CRM"],
            "risks": ["sin resumen curado todavía"],
            "case_type": "outbound_warm",
            "source_label": "Brevo deal deal-1",
        }

        status, headers, response = self.run_app(query_string="brevo_deal=deal-1")

        self.assertEqual(status, "200 OK")
        self.assertIn('value="Lucas Benites"', response)
        self.assertIn("outbound_warm", response)
        self.assertIn("Brevo deal deal-1", response)

    def test_get_can_load_curated_source_case(self):
        status, headers, response = self.run_app(query_string="curated_source=meet_discovery")

        self.assertEqual(status, "200 OK")
        self.assertIn("Resumen curado", response)
        self.assertIn("meet_discovery", response)
        self.assertIn("Discovery", response)


if __name__ == "__main__":
    unittest.main()
