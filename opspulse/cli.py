from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .analyzer import analyze
from .parser import parse_file
from .report import render_json, render_markdown


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="opspulse", description="Production incident triage from log files")
    subparsers = parser.add_subparsers(dest="command", required=True)
    analyze_parser = subparsers.add_parser("analyze", help="Analyze a log file")
    analyze_parser.add_argument("logfile", type=Path)
    analyze_parser.add_argument("--format", choices=("markdown", "json"), default="markdown")
    analyze_parser.add_argument("--output", type=Path)
    analyze_parser.add_argument("--window", type=int, default=5, metavar="MINUTES")
    analyze_parser.add_argument("--threshold", type=int, default=5, metavar="COUNT")
    analyze_parser.add_argument("--fail-score", type=int, default=60, metavar="SCORE")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.window < 1 or args.threshold < 1 or not 0 <= args.fail_score <= 100:
        print("error: window and threshold must be positive; fail-score must be 0-100", file=sys.stderr)
        return 1
    if not args.logfile.is_file():
        print(f"error: log file not found: {args.logfile}", file=sys.stderr)
        return 1

    try:
        events = parse_file(args.logfile)
        result = analyze(events, window_minutes=args.window, spike_threshold=args.threshold)
        content = (
            render_json(result)
            if args.format == "json"
            else render_markdown(result, source=str(args.logfile), window_minutes=args.window)
        )
        if args.output:
            args.output.write_text(content, encoding="utf-8")
            print(f"Report written to {args.output}")
        else:
            print(content, end="")
        return 0 if result.health_score >= args.fail_score else 2
    except OSError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

