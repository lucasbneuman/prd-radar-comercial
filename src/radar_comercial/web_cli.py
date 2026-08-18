from __future__ import annotations

import argparse
import os

from radar_comercial.web import serve


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="radar-comercial-web")
    parser.add_argument("--host", default=os.getenv("HOST", "0.0.0.0"))
    parser.add_argument("--port", type=int, default=int(os.getenv("PORT", "8008")))
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    serve(host=args.host, port=args.port)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
