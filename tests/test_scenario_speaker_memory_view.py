import json
from pathlib import Path

from audit import audit_runner


def test_speaker_memory_visualization_consistency():
    report = audit_runner.run_session("session1")
    features = report["features"]

    for key in ("diarization", "memory_profile", "speaker_view"):
        assert key in features
        available = json.loads(features[key]["availability"])
        assert available["status"].lower() in {"ok", "warn"}
