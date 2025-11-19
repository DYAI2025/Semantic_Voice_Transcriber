"""Command-line interface for SVT audit."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from .audit_runner import run_session
from .report_builder import build_report


def render_markdown(report: dict) -> str:
    lines = ["# SVT Feature Audit", "", f"Session: {report['session']}", ""]
    lines.append("| Feature | Readiness | Availability | Smoke |")
    lines.append("| --- | --- | --- | --- |")
    for key, data in report["features"].items():
        lines.append(
            f"| {data['name']} | {data['readiness']['label']} "
            f"| {data['availability']['status']} | {data['smoke']['status']} |"
        )
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Run SVT feature audit")
    parser.add_argument("--session", default="session1")
    parser.add_argument("--dataset", default="testdata")
    parser.add_argument("--json", default="reports/audit_report.json")
    parser.add_argument("--markdown", default="reports/audit_report.md")
    args = parser.parse_args()

    raw = run_session(args.session, Path(args.dataset))
    report = build_report(raw["features"], raw["session"])

    Path(args.json).parent.mkdir(parents=True, exist_ok=True)
    Path(args.json).write_text(json.dumps(report, indent=2), encoding="utf-8")

    md = render_markdown(report)
    Path(args.markdown).write_text(md, encoding="utf-8")
    print(f"✅ Reports saved to {args.json} and {args.markdown}")


if __name__ == "__main__":
    main()
