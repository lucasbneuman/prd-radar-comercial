from __future__ import annotations

import json
from datetime import datetime, UTC
from pathlib import Path


DEFAULT_RUNS_PATH = Path(__file__).resolve().parents[2] / "data" / "runs.jsonl"


def append_run(path: Path, *, case: dict, report: dict, source: str) -> dict:
    path.parent.mkdir(parents=True, exist_ok=True)
    record = {
        "created_at": datetime.now(UTC).isoformat(),
        "source": source,
        "case": case,
        "report": report,
    }
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=False) + "\n")
    return record


def load_runs(path: Path = DEFAULT_RUNS_PATH) -> list[dict]:
    if not path.exists():
        return []
    runs: list[dict] = []
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                runs.append(json.loads(line))
    return runs
