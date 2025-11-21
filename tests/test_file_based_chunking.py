import pytest
import json
import tempfile
from pathlib import Path
from audio_chunker import process_large_audio_with_chunking

def test_chunk_files_created_and_cleaned():
    """Verify temp chunk files are created and cleaned up"""
    # Mock transcribe function that returns minimal result
    def mock_transcribe(audio_path, **kwargs):
        return {
            'segments': [{'start': 0, 'end': 5, 'text': 'test'}],
            'prosody_features': [{'tempo_wpm': 120, 'pitch_mean_hz': 150, 'energy_rms': 0.05}],
            'speaker_segments': [],
            'overlapped_speech': [],
            'confidence_scores': {'segments': [], 'low_confidence_segments': []}
        }

    # Use small test audio (will be created in another task)
    test_audio = 'testdata/test_audio_10s.wav'

    # Skip if test audio doesn't exist
    if not Path(test_audio).exists():
        pytest.skip(f"Test audio file not available: {test_audio}")

    # Process with chunking
    result = process_large_audio_with_chunking(
        test_audio,
        mock_transcribe,
        chunk_duration=3.0,  # Small chunks for testing
        overlap_duration=0.5,
        cleanup_memory=True
    )

    # Verify result structure
    assert 'segments' in result
    assert len(result['segments']) > 0

    # Verify no temp files remain
    temp_dirs = list(Path('/tmp').glob('svt_chunks_*'))
    assert len(temp_dirs) == 0, "Temp directories should be cleaned up"

def test_incremental_memory_usage():
    """Verify memory doesn't accumulate during chunk processing"""
    import psutil
    import os

    test_audio = 'testdata/test_audio_10s.wav'

    # Skip if test audio doesn't exist
    if not Path(test_audio).exists():
        pytest.skip(f"Test audio file not available: {test_audio}")

    process = psutil.Process(os.getpid())
    initial_memory = process.memory_info().rss / 1024 / 1024  # MB

    def mock_transcribe(audio_path, **kwargs):
        # Simulate large chunk result (1000 segments)
        return {
            'segments': [{'start': i, 'end': i+1, 'text': f'segment {i}'} for i in range(1000)],
            'prosody_features': [{'tempo_wpm': 120} for _ in range(1000)],
            'speaker_segments': [],
            'overlapped_speech': [],
            'confidence_scores': {'segments': [], 'low_confidence_segments': []}
        }

    result = process_large_audio_with_chunking(
        test_audio,
        mock_transcribe,
        chunk_duration=2.0,
        overlap_duration=0.5,
        cleanup_memory=True
    )

    final_memory = process.memory_info().rss / 1024 / 1024  # MB
    memory_increase = final_memory - initial_memory

    # Memory increase should be < 100MB (not accumulated)
    assert memory_increase < 100, f"Memory increased by {memory_increase}MB (too much)"
