#!/usr/bin/env python3
"""Run DAST scans against a local test instance using OWASP ZAP baseline."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import textwrap
import threading
import time
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen

DEFAULT_ENDPOINTS = ("/api", "/health")
DEFAULT_SCANNER_CMD = (
    "docker run --rm --network host "
    "-v {report_dir}:/zap/wrk/:rw "
    "ghcr.io/zaproxy/zaproxy:stable "
    "zap-baseline.py -t {target} -J {json_report_name} -r {html_report_name} -m 3"
)


class _MinimalTestAppHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:  # noqa: N802 (http handler interface)
        if self.path in {"/health", "/api", "/"}:
            payload = json.dumps({"status": "ok", "path": self.path}).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
            return

        self.send_response(404)
        self.end_headers()

    def log_message(self, fmt: str, *args: object) -> None:  # silence default logging
        return


@dataclass
class RunningApp:
    base_url: str
    stop: Callable[[], None]


def _start_builtin_app(host: str, port: int) -> RunningApp:
    server = ThreadingHTTPServer((host, port), _MinimalTestAppHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    def _stop() -> None:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)

    return RunningApp(base_url=f"http://{host}:{port}", stop=_stop)


def _wait_for_endpoints(base_url: str, endpoints: Iterable[str], timeout_s: int) -> None:
    deadline = time.time() + timeout_s
    last_error = ""
    while time.time() < deadline:
        all_ready = True
        for endpoint in endpoints:
            try:
                with urlopen(f"{base_url.rstrip('/')}{endpoint}", timeout=2) as response:  # noqa: S310
                    if response.status >= 400:
                        all_ready = False
                        last_error = f"{endpoint} returned status {response.status}"
                        break
            except URLError as exc:
                all_ready = False
                last_error = f"{endpoint} not reachable: {exc}"
                break

        if all_ready:
            return
        time.sleep(1)

    raise RuntimeError(f"Application did not become healthy in {timeout_s}s. Last error: {last_error}")


def _run_scanner(
    scanner_cmd: str,
    target: str,
    report_dir: Path,
    json_report_name: str,
    html_report_name: str,
) -> None:
    format_vars = {
        "target": target,
        "report_dir": str(report_dir),
        "json_report_name": json_report_name,
        "html_report_name": html_report_name,
        "json_report": str(report_dir / json_report_name),
        "html_report": str(report_dir / html_report_name),
    }
    command = scanner_cmd.format(**format_vars)
    subprocess.run(command, check=True, shell=True)


def _parse_high_findings(report_path: Path) -> list[dict[str, str]]:
    data = json.loads(report_path.read_text(encoding="utf-8"))
    findings: list[dict[str, str]] = []

    for site in data.get("site", []):
        for alert in site.get("alerts", []):
            risk_code = int(alert.get("riskcode", "0"))
            risk_desc = str(alert.get("riskdesc", "Informational"))
            if risk_code >= 3 or "critical" in risk_desc.lower():
                findings.append(
                    {
                        "name": str(alert.get("name", "unknown")),
                        "risk": risk_desc,
                        "instances": str(len(alert.get("instances", []))),
                    }
                )

    return findings


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run OWASP ZAP baseline DAST scan.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=18080)
    parser.add_argument("--base-url", help="Base URL of an already-running app. Skips app startup when set.")
    parser.add_argument("--app-cmd", help="Command to start application under test in a test environment.")
    parser.add_argument(
        "--endpoints",
        nargs="+",
        default=list(DEFAULT_ENDPOINTS),
        help="Endpoints used for readiness checks.",
    )
    parser.add_argument("--timeout", type=int, default=60)
    parser.add_argument("--report-dir", default="artifacts/security")
    parser.add_argument("--json-report", default="dast-report.json")
    parser.add_argument("--html-report", default="dast-report.html")
    parser.add_argument(
        "--scanner-cmd",
        default=os.getenv("DAST_SCANNER_CMD", DEFAULT_SCANNER_CMD),
        help="Scanner command template. Supports {target}, {report_dir}, {json_report_name}, {html_report_name}, {json_report}, {html_report}.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report_dir = Path(args.report_dir)
    report_dir.mkdir(parents=True, exist_ok=True)

    app_process: subprocess.Popen[str] | None = None
    builtin_app: RunningApp | None = None

    try:
        if args.base_url:
            base_url = args.base_url.rstrip("/")
        elif args.app_cmd:
            app_process = subprocess.Popen(args.app_cmd, shell=True)  # noqa: S602
            base_url = f"http://{args.host}:{args.port}"
        else:
            builtin_app = _start_builtin_app(args.host, args.port)
            base_url = builtin_app.base_url

        _wait_for_endpoints(base_url, args.endpoints, args.timeout)

        _run_scanner(
            scanner_cmd=args.scanner_cmd,
            target=base_url,
            report_dir=report_dir,
            json_report_name=args.json_report,
            html_report_name=args.html_report,
        )

        findings = _parse_high_findings(report_dir / args.json_report)
        if findings:
            print("High/Critical DAST findings detected:")
            for finding in findings:
                print(f"- {finding['name']} ({finding['risk']}, instances={finding['instances']})")
            return 1

        print(
            textwrap.dedent(
                f"""
                DAST scan completed successfully.
                Reports:
                  - {report_dir / args.json_report}
                  - {report_dir / args.html_report}
                """
            ).strip()
        )
        return 0
    finally:
        if app_process is not None:
            app_process.terminate()
            try:
                app_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                app_process.kill()
        if builtin_app is not None:
            builtin_app.stop()


if __name__ == "__main__":
    sys.exit(main())
