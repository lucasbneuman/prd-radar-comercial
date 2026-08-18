from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from radar_comercial.analysis import analyze_case
from radar_comercial.presenter import render_report_markdown
from radar_comercial.run_store import DEFAULT_RUNS_PATH, append_run


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="radar-comercial-demo")
    parser.add_argument("--input", dest="input_path", help="Ruta a un JSON con el caso comercial")
    parser.add_argument("--format", choices=["markdown", "json"], default="markdown", help="Formato de salida")
    parser.add_argument("--no-persist", action="store_true", help="No guardar la corrida en el historial local")
    return parser


def load_case(input_path: str | None) -> dict:
    if input_path:
        return json.loads(Path(input_path).read_text(encoding="utf-8"))
    return json.load(sys.stdin)


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    case = load_case(args.input_path)
    report = analyze_case(case)
    if not args.no_persist:
        append_run(DEFAULT_RUNS_PATH, case=case, report=report, source="cli")
    if args.format == "json":
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(render_report_markdown(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
