"""
DEPRECATED: Use svt_core.audio.diarization instead.

This file provides backward compatibility.
Will be removed in version 2.0.
"""

import warnings

warnings.warn(
    "Importing from speaker_diarizer is deprecated. "
    "Use 'from svt_core.audio import SpeakerDiarizer' instead.",
    DeprecationWarning,
    stacklevel=2
)

from svt_core.audio.diarization import SpeakerDiarizer

__all__ = ['SpeakerDiarizer']
