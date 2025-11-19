"""Checks for prosody extraction module."""
from __future__ import annotations

from typing import Dict, TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:  # pragma: no cover
    from audit.feature_registry import FeatureMetadata

TEST_AUDIO_LEN = 16000  # 1 second synthetic signal


def prosody_availability(meta: "FeatureMetadata") -> Dict[str, str]:
    try:
        from prosody_extractor import ProsodyExtractor  # noqa
        extractor = ProsodyExtractor()
        return {"status": "ok", "details": f"sample_rate={extractor.sample_rate}"}
    except Exception as exc:
        return {"status": "error", "details": str(exc)}


def prosody_smoke(meta: "FeatureMetadata") -> Dict[str, str]:
    try:
        from prosody_extractor import ProsodyExtractor  # noqa

        extractor = ProsodyExtractor()
        audio = np.zeros(TEST_AUDIO_LEN, dtype=np.float32)
        features = extractor.extract_segment_features(audio, 0.0, 1.0, text="Test")
        assert features.duration == 1.0
        return {"status": "pass", "details": "segment duration 1.0"}
    except Exception as exc:
        return {"status": "fail", "details": str(exc)}
