"""
DEPRECATED: Use svt_core.audio.preprocessing instead.

This file provides backward compatibility.
Will be removed in version 2.0.
"""

import warnings

warnings.warn(
    "Importing from audio_preprocessor is deprecated. "
    "Use 'from svt_core.audio import AudioPreprocessor' instead.",
    DeprecationWarning,
    stacklevel=2
)

from svt_core.audio.preprocessing import AudioPreprocessor

__all__ = ['AudioPreprocessor']
