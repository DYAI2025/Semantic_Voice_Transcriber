import json
from pathlib import Path

from audit import audit_runner


def test_emotion_turning_point_alignment(tmp_path):
    report = audit_runner.run_session("session1")
    features = report["features"]

    for key in ("emotions", "prosody", "turning_points", "dual_markers"):
        assert key in features
        assert "status" in json.loads(features[key]["availability"])

    # Ensure outputs are not empty place-holders
    assert json.loads(features["emotions"]["smoke"])["status"] != "fail"
    assert json.loads(features["prosody"]["smoke"])["status"] != "fail"
