#!/usr/bin/env python3
"""Run Bandit and fail when high-severity issues are detected."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

HIGH_SEVERITY = {"HIGH"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Bandit static security scan.")
    parser.add_argument("--target", default=".", help="Directory or file to scan")
    parser.add_argument("--report", default="artifacts/security/bandit-report.json")
    parser.add_argument("--exclude", default=".venv,venv,node_modules")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report_path = Path(args.report)
    report_path.parent.mkdir(parents=True, exist_ok=True)

    command = [
        "bandit",
        "-r",
        args.target,
        "-f",
        "json",
        "-o",
        str(report_path),
        "--severity-level",
        "high",
        "--exclude",
        args.exclude,
    ]
    result = subprocess.run(command, check=False)

    if not report_path.exists():
        print("Bandit did not produce a report.", file=sys.stderr)
        return result.returncode or 1

    data = json.loads(report_path.read_text(encoding="utf-8"))
    findings = [
        issue
        for issue in data.get("results", [])
        if str(issue.get("issue_severity", "")).upper() in HIGH_SEVERITY
    ]

    if findings:
        print(f"Found {len(findings)} high-severity Bandit issue(s).")
        return 1

    print(f"Bandit completed with no high-severity findings. Report: {report_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
