from audit.readiness import ReadinessInputs, compute_readiness, ReadinessLevel


def test_compute_readiness_levels():
    assert compute_readiness(ReadinessInputs("ok", "pass", [])) == ReadinessLevel.PILOT_READY
    assert compute_readiness(ReadinessInputs("warn", "pass", [])) == ReadinessLevel.NOT_AVAILABLE
    assert compute_readiness(ReadinessInputs("ok", "fail", [])) == ReadinessLevel.LIMITED
    assert compute_readiness(ReadinessInputs("ok", "pass", ["issue"])) == ReadinessLevel.READY_WITH_WARNINGS
