"""
Audio Processing Module

Provides audio quality analysis, preprocessing, prosody extraction,
and speaker diarization functionality for Semantic Voice Transcriber.

Modules:
    - quality: Audio quality analysis (SNR, quality metrics)
    - preprocessing: Audio preprocessing (noise reduction, normalization)
    - prosody: Prosody extraction (Big 4: Tempo, Pitch, Energy, Pauses)
    - diarization: Speaker diarization (pyannote.audio integration)
    - diarization_cpu: CPU-only diarization fallback

Usage:
    from svt_core.audio import (
        AudioQualityAnalyzer,
        AudioPreprocessor,
        ProsodyExtractor,
        SpeakerDiarizer,
        CPUDiarizer,
    )
"""

# Import all migrated modules
from .quality import AudioQualityAnalyzer
from .preprocessing import AudioPreprocessor
from .prosody import ProsodyExtractor
from .diarization import SpeakerDiarizer
from .diarization_cpu import CPUDiarizer

__all__ = [
    'AudioQualityAnalyzer',       # Phase 2.2 ✅
    'AudioPreprocessor',          # Phase 2.3 ✅
    'ProsodyExtractor',           # Phase 2.4 ✅
    'SpeakerDiarizer',            # Phase 2.5 ✅
    'CPUDiarizer',                # Already migrated
]

__version__ = '1.0.0'
__author__ = 'SVT Development Team'
