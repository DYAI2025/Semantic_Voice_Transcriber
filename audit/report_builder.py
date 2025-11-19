"""Utilities for assembling audit reports."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict

import jsonschema

from audit.feature_registry import FEATURE_REGISTRY
from audit.readiness import ReadinessInputs, compute_readiness

SCHEMA_PATH = Path(__file__).with_name("schemas") / "audit_report.schema.json"


def build_report(results: Dict[str, Dict[str, Dict[str, str]]], session: str) -> Dict[str, object]:
    features = {}
    for key, data in results.items():
        availability = json.loads(data["availability"]) if isinstance(data["availability"], str) else data["availability"]
        smoke = json.loads(data["smoke"]) if isinstance(data["smoke"], str) else data["smoke"]
        readiness = compute_readiness(ReadinessInputs(
            availability_status=availability.get("status", "unknown"),
            smoke_status=smoke.get("status", "not_run"),
            issues=[],
        ))
        features[key] = {
            "name": FEATURE_REGISTRY[key].name,
            "availability": availability,
            "smoke": smoke,
            "readiness": {"level": readiness.value, "label": readiness.label()},
            "issues": [],
        }
    report = {
        "session": session,
        "metadata": {"timestamp": datetime.now(timezone.utc).isoformat()},
        "features": features,
    }
    _validate(report)
    return report


def _validate(report: Dict[str, object]):
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    jsonschema.validate(report, schema)
