import io
import unittest
from wsgiref.util import setup_testing_defaults

from radar_comercial.web import app


class CrmDemoViewTest(unittest.TestCase):
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

    def test_get_renders_internal_crm_demo_section(self):
        status, headers, response = self.run_app()

        self.assertEqual(status, "200 OK")
        self.assertEqual(headers["Content-Type"], "text/html; charset=utf-8")
        self.assertIn("CRM demo interno", response)
        self.assertIn("Leads demo", response)
        self.assertIn("Apex Analytics", response)
        self.assertIn("Nexa Studio", response)

    def test_get_can_open_demo_lead_and_prefill_case(self):
        status, headers, response = self.run_app(query_string="lead_id=lead-apex")

        self.assertEqual(status, "200 OK")
        self.assertIn("Ficha del lead", response)
        self.assertIn("Apex Analytics", response)
        self.assertIn("Operación trabada por seguimiento manual", response)
        self.assertIn('value="Apex Analytics"', response)
        self.assertIn("CRM demo · Apex Analytics", response)
        self.assertIn("Ver informe general", response)

    def test_get_can_focus_specific_source_from_demo_lead(self):
        status, headers, response = self.run_app(query_string="lead_id=lead-apex&source_id=src-apex-whatsapp")

        self.assertEqual(status, "200 OK")
        self.assertIn("WhatsApp", response)
        self.assertIn("CRM demo · WhatsApp · Apex Analytics", response)
        self.assertIn("pidió propuesta aterrizada para 3 vendedores", response)
        self.assertIn('value="Apex Analytics"', response)


if __name__ == "__main__":
    unittest.main()
