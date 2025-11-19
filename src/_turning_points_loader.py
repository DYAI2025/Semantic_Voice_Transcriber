"""Helpers for accessing the full turning-point detector stack when available."""
from __future__ import annotations

import importlib
import sys
from pathlib import Path
from types import ModuleType
from typing import Optional

_DETECTOR_ROOT = (
    Path(__file__).resolve().parents[1]
    / "Turning_Points_in_Transcription"
    / "turning_points_detector"
)
_SYS_PATH_READY = False
_PACKAGE_PREFIX = "turning_points_detector.src"


def _ensure_sys_path() -> bool:
    """Make sure the detector root is on sys.path so namespace packages work."""
    global _SYS_PATH_READY
    if _SYS_PATH_READY:
        return True
    if not _DETECTOR_ROOT.exists():
        return False
    parent = _DETECTOR_ROOT.parent
    root_str = str(parent)
    if root_str not in sys.path:
        sys.path.insert(0, root_str)
    _SYS_PATH_READY = True
    return True


def load_module(relative_module: str) -> Optional[ModuleType]:
    """Import a module from the turning-point detector package if available."""
    if not _ensure_sys_path():
        return None
    full_name = f"{_PACKAGE_PREFIX}.{relative_module}"
    try:
        return importlib.import_module(full_name)
    except ModuleNotFoundError:
        return None
