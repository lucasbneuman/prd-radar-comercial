import json
import tempfile
import unittest
from pathlib import Path

from radar_comercial.run_store import append_run, load_runs


class RunStoreTest(unittest.TestCase):
    def test_appends_and_reads_runs_from_jsonl(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "runs.jsonl"
            append_run(
                path,
                case={"company": "Acme", "objective": "ordenar pipeline comercial"},
                report={"priority": "alta", "summary": "Acme necesita ordenar pipeline comercial."},
                source="cli",
            )
            append_run(
                path,
                case={"company": "Beta", "objective": "mejorar seguimiento"},
                report={"priority": "media", "summary": "Beta necesita mejorar seguimiento."},
                source="web",
            )

            runs = load_runs(path)

        self.assertEqual(len(runs), 2)
        self.assertEqual(runs[0]["source"], "cli")
        self.assertEqual(runs[1]["case"]["company"], "Beta")
        self.assertIn("created_at", runs[0])


if __name__ == "__main__":
    unittest.main()
