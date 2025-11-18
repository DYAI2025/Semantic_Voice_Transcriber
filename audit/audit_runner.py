"""Audit runner CLI."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict

from .feature_registry import FEATURE_REGISTRY, FeatureMetadata

DEFAULT_DATASET = Path("testdata")


def run_session(session_id: str, dataset_dir: Path = DEFAULT_DATASET) -> Dict[str, Dict[str, str]]:
    transcript_path = dataset_dir / "transcripts" / f"{session_id}.json"
    audio_path = dataset_dir / "audio" / f"{session_id}.wav"
    if not transcript_path.exists() or not audio_path.exists():
        raise FileNotFoundError(f"Missing dataset for session {session_id}")

    results: Dict[str, Dict[str, str]] = {}
    for key, meta in FEATURE_REGISTRY.items():
        avail = meta.availability_check(meta)
        smoke = meta.smoke_test(meta)
        results[key] = {
            "name": meta.name,
            "availability": json.dumps(avail),
            "smoke": json.dumps(smoke),
        }
    return {
        "session": session_id,
        "audio": str(audio_path),
        "transcript": str(transcript_path),
        "features": results,
    }


def cli():
    parser = argparse.ArgumentParser(description="Run SVT feature audit")
    parser.add_argument("--session", default="session1")
    parser.add_argument("--dataset", default=str(DEFAULT_DATASET))
    parser.add_argument("--output", default="audit_report.json")
    args = parser.parse_args()

    report = run_session(args.session, Path(args.dataset))
    Path(args.output).write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"✅ Audit report written to {args.output}")


if __name__ == "__main__":
    cli()
