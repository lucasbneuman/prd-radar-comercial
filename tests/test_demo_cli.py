import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from radar_comercial.demo_cli import main


class DemoCliTest(unittest.TestCase):
    def test_reads_case_from_input_file(self):
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
                exit_code = main(["--input", str(path)])

        output = buffer.getvalue()
        self.assertEqual(exit_code, 0)
        self.assertIn("# Radar Comercial", output)
        self.assertIn("Acme necesita ordenar pipeline comercial.", output)


if __name__ == "__main__":
    unittest.main()
