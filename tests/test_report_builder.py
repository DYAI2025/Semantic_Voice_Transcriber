import json
from audit import audit_runner
from audit.report_builder import build_report


def test_report_builder_schema(tmp_path):
    raw = audit_runner.run_session("session1")
    report = build_report(raw["features"], raw["session"])
    assert "features" in report
    for data in report["features"].values():
        assert "readiness" in data
        assert isinstance(data["readiness"]["level"], int)
