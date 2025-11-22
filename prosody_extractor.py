"""
DEPRECATED: Use svt_core.audio.prosody instead.

This file provides backward compatibility.
Will be removed in version 2.0.
"""

import warnings

warnings.warn(
    "Importing from prosody_extractor is deprecated. "
    "Use 'from svt_core.audio import ProsodyExtractor' instead.",
    DeprecationWarning,
    stacklevel=2
)

from svt_core.audio.prosody import ProsodyExtractor

__all__ = ['ProsodyExtractor']
