"""
DEPRECATED: Use svt_core.audio.quality instead.

This file provides backward compatibility.
Will be removed in version 2.0.
"""

import warnings

warnings.warn(
    "Importing from audio_quality_analyzer is deprecated. "
    "Use 'from svt_core.audio import AudioQualityAnalyzer' instead.",
    DeprecationWarning,
    stacklevel=2
)

from svt_core.audio.quality import AudioQualityAnalyzer

__all__ = ['AudioQualityAnalyzer']
