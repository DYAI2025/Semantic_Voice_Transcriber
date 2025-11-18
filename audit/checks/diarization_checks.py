"""Checks for speaker diarization."""
from __future__ import annotations

from typing import Dict, TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from audit.feature_registry import FeatureMetadata


def diarization_availability(meta: "FeatureMetadata") -> Dict[str, str]:
    try:
        from speaker_diarizer import SpeakerDiarizer  # noqa
        return {"status": "ok", "details": "pyannote available"}
    except Exception as exc:
        return {"status": "warn", "details": f"pyannote unavailable: {exc}"}


def diarization_smoke(meta: "FeatureMetadata") -> Dict[str, str]:
    try:
        from svt_core.audio.diarization_cpu import CPUDiarizer  # noqa

        cpu = CPUDiarizer()
        segments = cpu.diarize(Path("testdata/audio/session1.wav"))
        if segments:
            return {"status": "pass", "details": f"segments={len(segments)}"}
        return {"status": "warn", "details": "no segments produced"}
    except Exception as exc:
        return {"status": "fail", "details": str(exc)}
