import io
import json
import unittest
from urllib.parse import quote_plus
from wsgiref.util import setup_testing_defaults

from radar_comercial.web import app


class WebEnhancementsTest(unittest.TestCase):
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

    def test_get_loads_example_case_into_form(self):
        status, headers, response = self.run_app(query_string="example=high-intent-case.json")

        self.assertEqual(status, "200 OK")
        self.assertEqual(headers["Content-Type"], "text/html; charset=utf-8")
        self.assertIn('value="Acme"', response)
        self.assertIn("inbound_hot", response)

    def test_post_can_export_json_response(self):
        body = (
            "company=Acme&objective=ordenar+pipeline+comercial"
            "&pain_points=seguimiento+manual"
            "&signals=pidi%C3%B3+demo+esta+semana"
            "&risks=no+tiene+proceso+consistente"
            "&case_type=inbound_hot"
            "&response_format=json"
        )
        status, headers, response = self.run_app(method="POST", body=body)

        self.assertEqual(status, "200 OK")
        self.assertEqual(headers["Content-Type"], "application/json; charset=utf-8")
        payload = json.loads(response)
        self.assertEqual(payload["priority"], "alta")
        self.assertEqual(payload["case_type"], "inbound_hot")


if __name__ == "__main__":
    unittest.main()
