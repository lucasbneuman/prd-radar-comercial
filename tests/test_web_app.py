import io
import unittest
from wsgiref.util import setup_testing_defaults

from radar_comercial.web import app


class WebAppTest(unittest.TestCase):
    def run_app(self, method="GET", body=""):
        environ = {}
        setup_testing_defaults(environ)
        environ["REQUEST_METHOD"] = method
        payload = body.encode("utf-8")
        environ["CONTENT_LENGTH"] = str(len(payload))
        environ["wsgi.input"] = io.BytesIO(payload)

        captured = {}

        def start_response(status, headers):
            captured["status"] = status
            captured["headers"] = headers

        response = b"".join(app(environ, start_response)).decode("utf-8")
        return captured["status"], dict(captured["headers"]), response

    def test_get_returns_html_form(self):
        status, headers, response = self.run_app()

        self.assertEqual(status, "200 OK")
        self.assertEqual(headers["Content-Type"], "text/html; charset=utf-8")
        self.assertIn("<form", response)
        self.assertIn("Radar Comercial", response)
        self.assertIn("name=\"company\"", response)

    def test_post_renders_report_from_form_data(self):
        body = (
            "company=Acme&objective=ordenar+pipeline+comercial"
            "&pain_points=seguimiento+manual%0Aoportunidades+sin+prioridad+clara"
            "&signals=pidi%C3%B3+demo+esta+semana%0Aequipo+comercial+activo"
            "&risks=no+tiene+proceso+consistente"
            "&case_type=inbound_hot"
        )
        status, headers, response = self.run_app(method="POST", body=body)

        self.assertEqual(status, "200 OK")
        self.assertEqual(headers["Content-Type"], "text/html; charset=utf-8")
        self.assertIn("Acme necesita ordenar pipeline comercial.", response)
        self.assertIn("Prioridad", response)
        self.assertIn("inbound_hot", response)
        self.assertIn("Agendar demo enfocada en prioridades y siguientes pasos.", response)


if __name__ == "__main__":
    unittest.main()
