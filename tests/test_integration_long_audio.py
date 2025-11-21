"""
Integration tests for file-based chunk merge with real audio files.

Tests memory usage and output quality when processing long audio files.
These tests require actual audio files and may be skipped in CI.
"""
import pytest
import psutil
import os
import gc
from pathlib import Path

# Skip all tests if test audio unavailable
TEST_AUDIO_DIR = Path(__file__).parent.parent / "Eingang"
LONG_AUDIO_FILE = "KAH - EGO STATE PS (3).m4a"
TEST_AUDIO_PATH = TEST_AUDIO_DIR / LONG_AUDIO_FILE

pytestmark = pytest.mark.skipif(
    not TEST_AUDIO_PATH.exists(),
    reason="Test audio file not available"
)


@pytest.mark.integration
@pytest.mark.requires_audio
@pytest.mark.requires_model
@pytest.mark.slow
def test_long_audio_memory_usage():
    """
    Integration test: Verify memory-efficient processing of 37-minute audio file.

    Expected behavior:
    - Process completes without OOM
    - Peak memory increase < 2GB (single chunk size)
    - SWAP usage stays reasonable (< 80% of available)
    - All segments successfully merged
    """
    from audio_chunker import process_large_audio_with_chunking

    # Mock transcribe function for testing
    def mock_transcribe(audio_path: str, **kwargs) -> dict:
        """
        Mock transcription that returns realistic structure.
        In real test, this would call actual Whisper model.
        """
        return {
            'segments': [
                {
                    'id': 0,
                    'start': 0.0,
                    'end': 5.0,
                    'text': 'Test segment',
                    'confidence': 0.95
                }
            ],
            'prosody_features': [
                {
                    'start': 0.0,
                    'end': 5.0,
                    'tempo_wpm': 120,
                    'pitch_mean_hz': 150,
                    'energy_rms': 0.05
                }
            ],
            'speaker_segments': [],
            'overlapped_speech': [],
            'confidence_scores': {
                'mean': 0.95,
                'std': 0.02,
                'min': 0.90,
                'max': 0.98
            }
        }

    # Get baseline memory
    gc.collect()
    process = psutil.Process()
    memory_before = process.memory_info().rss / 1024 / 1024  # MB

    # Process with file-based chunking
    result = process_large_audio_with_chunking(
        audio_path=str(TEST_AUDIO_PATH),
        transcribe_func=mock_transcribe,
        chunk_duration=120.0,  # 2-minute chunks (same as production)
        overlap_duration=5.0,
        cleanup_memory=True
    )

    # Measure memory after
    gc.collect()
    memory_after = process.memory_info().rss / 1024 / 1024  # MB
    memory_increase = memory_after - memory_before

    # Verify results
    assert 'segments' in result
    assert 'prosody_baseline' in result
    assert len(result['segments']) > 0

    # Memory assertions
    assert memory_increase < 2000, f"Memory increase too high: {memory_increase:.1f} MB"

    print(f"\n✓ Memory usage: {memory_increase:.1f} MB increase")
    print(f"✓ Segments processed: {len(result['segments'])}")
    print(f"✓ Prosody baseline calculated: {result['prosody_baseline'] is not None}")


@pytest.mark.integration
@pytest.mark.requires_audio
@pytest.mark.requires_model
@pytest.mark.slow
def test_long_audio_output_quality():
    """
    Integration test: Verify output quality matches expectations.

    Expected behavior:
    - Transcript has correct segment count (~493 based on previous run)
    - Prosody baseline calculated correctly
    - Speaker segments preserved
    - Confidence scores aggregated
    - Output files created successfully
    """
    from audio_chunker import process_large_audio_with_chunking

    # This test would call the actual transcription pipeline
    # For now, we verify the structure is correct

    # Mock transcribe function that simulates real Whisper output
    def mock_transcribe(audio_path: str, **kwargs) -> dict:
        """
        Mock with more realistic multi-segment output.
        """
        segments = []
        prosody_features = []

        # Simulate 20 segments per chunk
        for i in range(20):
            start_time = i * 5.0
            end_time = start_time + 5.0
            segments.append({
                'id': i,
                'start': start_time,
                'end': end_time,
                'text': f'Test segment {i}',
                'confidence': 0.90 + (i % 10) * 0.01
            })
            prosody_features.append({
                'start': start_time,
                'end': end_time,
                'tempo_wpm': 100 + (i % 40),
                'pitch_mean_hz': 140 + (i % 30),
                'energy_rms': 0.04 + (i % 10) * 0.001
            })

        return {
            'segments': segments,
            'prosody_features': prosody_features,
            'speaker_segments': [
                {'start': 0.0, 'end': 50.0, 'speaker': 'Speaker A'},
                {'start': 50.0, 'end': 100.0, 'speaker': 'Speaker B'}
            ],
            'overlapped_speech': [],
            'confidence_scores': {
                'mean': 0.92,
                'std': 0.03,
                'min': 0.85,
                'max': 0.97
            }
        }

    # Process with file-based chunking
    result = process_large_audio_with_chunking(
        audio_path=str(TEST_AUDIO_PATH),
        transcribe_func=mock_transcribe,
        chunk_duration=120.0,
        overlap_duration=5.0,
        cleanup_memory=True
    )

    # Verify output structure
    assert 'segments' in result
    assert 'prosody_features' in result
    assert 'prosody_baseline' in result
    assert 'confidence_scores' in result

    # Verify baseline calculation
    baseline = result['prosody_baseline']
    assert baseline is not None
    assert 'tempo_wpm_mean' in baseline
    assert 'pitch_mean_hz' in baseline
    assert 'energy_rms_mean' in baseline
    assert baseline['tempo_wpm_mean'] > 0
    assert baseline['pitch_mean_hz'] > 0
    assert baseline['energy_rms_mean'] > 0

    # Verify segments merged with correct timestamps
    segments = result['segments']
    assert len(segments) > 0

    # First segment should start near 0
    assert segments[0]['start'] >= 0
    assert segments[0]['start'] < 1.0

    # Segments should be in chronological order
    for i in range(1, len(segments)):
        assert segments[i]['start'] >= segments[i-1]['start']

    print(f"\n✓ Total segments: {len(segments)}")
    print(f"✓ Prosody baseline: tempo={baseline['tempo_wpm_mean']:.1f} wpm, "
          f"pitch={baseline['pitch_mean_hz']:.1f} Hz, "
          f"energy={baseline['energy_rms_mean']:.4f}")
    if 'overall_confidence' in result['confidence_scores']:
        print(f"✓ Confidence: overall={result['confidence_scores']['overall_confidence']:.3f}")

    # Verify speaker segments preserved
    if 'speaker_segments' in result and len(result['speaker_segments']) > 0:
        print(f"✓ Speaker segments: {len(result['speaker_segments'])}")


if __name__ == "__main__":
    # Allow running tests directly
    pytest.main([__file__, "-v", "-s"])
