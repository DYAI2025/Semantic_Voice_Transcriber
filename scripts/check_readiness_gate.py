#!/usr/bin/env python3
"""Fail if critical features have readiness < 2."""
from __future__ import annotations

import json
import sys
from pathlib import Path

CRITICAL_FEATURES = {"prosody", "diarization", "emotions"}


def main(path: str):
    report = json.loads(Path(path).read_text(encoding="utf-8"))
    failed = []
    for key in CRITICAL_FEATURES:
        feature = report["features"].get(key)
        if not feature:
            failed.append(f"missing feature {key}")
            continue
        level = feature["readiness"]["level"]
        if level < 2:
            failed.append(f"{key} readiness {level}")
    if failed:
        print("❌ Readiness gate failed:")
        for msg in failed:
            print(" -", msg)
        sys.exit(1)
    print("✅ Readiness gate passed")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit("Usage: check_readiness_gate.py <report.json>")
    main(sys.argv[1])
