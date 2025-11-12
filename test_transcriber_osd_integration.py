#!/usr/bin/env python3
import pytest
from pathlib import Path
from auto_transcriber_v4_emotion import transcribe_with_whisper
import os

HF_TOKEN = os.getenv('HF_TOKEN')
TEST_AUDIO = Path("Eingang/Patient/KAH EGOSTATE (2).m4a")

pytestmark = pytest.mark.skipif(
    not HF_TOKEN or not TEST_AUDIO.exists(),
    reason="HF_TOKEN or test audio not available"
)


def test_transcribe_with_osd_enabled():
    """Test transcription with OSD returns overlap segments"""
    result = transcribe_with_whisper(
        audio_path=str(TEST_AUDIO),
        model_size='tiny',
        language='de',
        enable_diarization=False,
        enable_overlap_detection=True,  # NEW PARAMETER
        hf_token=HF_TOKEN
    )

    assert 'overlapped_speech' in result
    assert isinstance(result['overlapped_speech'], list)


def test_transcribe_segments_have_overlap_flag():
    """Test segments are flagged if they overlap with detected regions"""
    result = transcribe_with_whisper(
        audio_path=str(TEST_AUDIO),
        model_size='tiny',
        language='de',
        enable_overlap_detection=True,
        hf_token=HF_TOKEN
    )

    # Check if any segment has overlap marker
    segments = result.get('segments', [])
    # At least one segment should have 'has_overlap' field
    assert any('has_overlap' in seg for seg in segments)
