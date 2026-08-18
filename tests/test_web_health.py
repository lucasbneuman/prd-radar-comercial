import io
import unittest
from wsgiref.util import setup_testing_defaults

from radar_comercial.web import app


class WebHealthTest(unittest.TestCase):
    def test_health_returns_ok_json(self):
        environ = {}
        setup_testing_defaults(environ)
        environ["REQUEST_METHOD"] = "GET"
        environ["PATH_INFO"] = "/health"
        environ["wsgi.input"] = io.BytesIO(b"")
        environ["CONTENT_LENGTH"] = "0"

        captured = {}

        def start_response(status, headers):
            captured["status"] = status
            captured["headers"] = dict(headers)

        payload = b"".join(app(environ, start_response)).decode("utf-8")

        self.assertEqual(captured["status"], "200 OK")
        self.assertEqual(captured["headers"]["Content-Type"], "application/json; charset=utf-8")
        self.assertEqual(payload, '{"status":"ok"}')


if __name__ == "__main__":
    unittest.main()
