"""Checks for Memory profile components."""
from __future__ import annotations

from pathlib import Path
from typing import Dict, TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from audit.feature_registry import FeatureMetadata

MEMORY_DIR = Path("Memory")


def memory_availability(meta: "FeatureMetadata") -> Dict[str, str]:
    try:
        from psychoanalysis_cache import CacheManager  # noqa
        if not MEMORY_DIR.exists():
            return {"status": "warn", "details": "Memory directory missing"}
        return {"status": "ok", "details": "Memory modules importable"}
    except Exception as exc:
        return {"status": "error", "details": str(exc)}


def memory_smoke(meta: "FeatureMetadata") -> Dict[str, str]:
    try:
        from psychoanalysis_cache import CacheManager  # noqa

        cache = CacheManager(cache_dir="Memory/test_cache")
        dummy_data = {"utterances": []}
        key = cache.compute_cache_key(dummy_data)
        cache.save_analysis(dummy_data, {"utterance_states": []})
        _ = cache.get_cached_analysis(dummy_data)
        (Path(cache.cache_dir) / f"{key}.json").unlink(missing_ok=True)
        return {"status": "pass", "details": "Cache read/write ok"}
    except Exception as exc:
        return {"status": "fail", "details": str(exc)}
