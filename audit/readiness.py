"""Readiness scoring helpers."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import List


class ReadinessLevel(Enum):
    NOT_AVAILABLE = 0
    LIMITED = 1
    READY_WITH_WARNINGS = 2
    PILOT_READY = 3

    def label(self) -> str:
        labels = {
            ReadinessLevel.NOT_AVAILABLE: "not available",
            ReadinessLevel.LIMITED: "limited",
            ReadinessLevel.READY_WITH_WARNINGS: "ready (warnings)",
            ReadinessLevel.PILOT_READY: "pilot ready",
        }
        return labels[self]


@dataclass
class ReadinessInputs:
    availability_status: str
    smoke_status: str
    issues: List[str]


def compute_readiness(inputs: ReadinessInputs) -> ReadinessLevel:
    avail = inputs.availability_status.lower()
    smoke = inputs.smoke_status.lower()
    issue_count = len(inputs.issues)

    if avail != "ok":
        return ReadinessLevel.NOT_AVAILABLE
    if smoke not in {"pass", "ok"}:
        return ReadinessLevel.LIMITED
    if issue_count:
        return ReadinessLevel.READY_WITH_WARNINGS
    return ReadinessLevel.PILOT_READY
