import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from radar_comercial.demo_cli import main


class DemoCliFormatsTest(unittest.TestCase):
    def test_renders_json_output_when_requested(self):
        case = {
            "company": "Acme",
            "objective": "ordenar pipeline comercial",
            "pain_points": ["seguimiento manual"],
            "signals": ["pidió demo esta semana"],
            "risks": ["no tiene proceso consistente"],
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "case.json"
            path.write_text(json.dumps(case), encoding="utf-8")
            buffer = io.StringIO()

            with redirect_stdout(buffer):
                exit_code = main(["--input", str(path), "--format", "json"])

        output = json.loads(buffer.getvalue())
        self.assertEqual(exit_code, 0)
        self.assertEqual(output["summary"], "Acme necesita ordenar pipeline comercial.")
        self.assertEqual(output["priority"], "alta")
        self.assertIn("confidence", output)


if __name__ == "__main__":
    unittest.main()
