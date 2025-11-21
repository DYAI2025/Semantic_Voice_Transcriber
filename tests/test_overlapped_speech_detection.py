#!/usr/bin/env python3
import pytest
from pathlib import Path
from speaker_diarizer import SpeakerDiarizer
import os

# Skip if no HF token available
HF_TOKEN = os.getenv('HF_TOKEN')
pytestmark = pytest.mark.skipif(
    not HF_TOKEN,
    reason="HF_TOKEN not set"
)


def test_overlapped_speech_detection_initialization():
    """Test OSD pipeline can be initialized"""
    diarizer = SpeakerDiarizer(use_auth_token=HF_TOKEN)
    diarizer._load_osd_pipeline()

    assert diarizer.osd_pipeline is not None


def test_detect_overlapped_speech_returns_segments():
    """Test OSD returns list of overlap segments"""
    diarizer = SpeakerDiarizer(use_auth_token=HF_TOKEN)

    # Use test audio file (create dummy if needed)
    test_audio = Path("test_audio_overlap.wav")
    if not test_audio.exists():
        pytest.skip("Test audio not available")

    overlaps = diarizer.detect_overlapped_speech(
        test_audio,
        min_duration_on=0.0,
        min_duration_off=0.0
    )

    assert isinstance(overlaps, list)
    # Each overlap has start, end, duration
    if len(overlaps) > 0:
        assert 'start' in overlaps[0]
        assert 'end' in overlaps[0]
        assert 'duration' in overlaps[0]


def test_overlapped_speech_output_format():
    """Test overlap segments have correct format"""
    diarizer = SpeakerDiarizer(use_auth_token=HF_TOKEN)
    test_audio = Path("test_audio_overlap.wav")

    if not test_audio.exists():
        pytest.skip("Test audio not available")

    overlaps = diarizer.detect_overlapped_speech(test_audio)

    for overlap in overlaps:
        assert overlap['start'] >= 0
        assert overlap['end'] > overlap['start']
        assert overlap['duration'] == overlap['end'] - overlap['start']
        assert 'overlap_type' in overlap  # e.g., "simultaneous_speech"
