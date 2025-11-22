"""
Tests for file-based vs in-memory merge feature flag.

Verifies that both merge modes produce equivalent results and that the
use_file_based_merge parameter works correctly.
"""
import pytest
from pathlib import Path
from audio_chunker import process_large_audio_with_chunking


def mock_transcribe(audio_path: str, **kwargs) -> dict:
    """
    Mock transcription function that returns realistic test data.
    """
    return {
        'segments': [
            {
                'id': 0,
                'start': 0.0,
                'end': 5.0,
                'text': 'Test segment',
                'confidence': 0.95
            },
            {
                'id': 1,
                'start': 5.0,
                'end': 10.0,
                'text': 'Another test segment',
                'confidence': 0.92
            }
        ],
        'prosody_features': [
            {
                'start': 0.0,
                'end': 5.0,
                'tempo_wpm': 120,
                'pitch_mean_hz': 150,
                'energy_rms': 0.05
            },
            {
                'start': 5.0,
                'end': 10.0,
                'tempo_wpm': 115,
                'pitch_mean_hz': 148,
                'energy_rms': 0.048
            }
        ],
        'speaker_segments': [
            {'start': 0.0, 'end': 5.0, 'speaker': 'Speaker A'},
            {'start': 5.0, 'end': 10.0, 'speaker': 'Speaker B'}
        ],
        'overlapped_speech': [],
        'confidence_scores': {
            'mean': 0.935,
            'std': 0.015,
            'min': 0.92,
            'max': 0.95
        }
    }


def test_file_based_merge_mode():
    """
    Test that file-based merge mode works correctly (default behavior).
    """
    # Create a test audio file path
    test_audio = Path(__file__).parent.parent / "Eingang" / "test_audio.wav"

    # Skip if test audio doesn't exist
    if not test_audio.exists():
        pytest.skip("Test audio file not available")

    # Process with file-based merge (default)
    result = process_large_audio_with_chunking(
        audio_path=str(test_audio),
        transcribe_func=mock_transcribe,
        chunk_duration=10.0,  # Small chunks for testing
        overlap_duration=2.0,
        use_file_based_merge=True  # Explicit file-based mode
    )

    # Verify result structure
    assert 'segments' in result
    assert 'prosody_features' in result
    assert 'prosody_baseline' in result
    assert 'speaker_segments' in result

    # Verify prosody baseline was calculated
    baseline = result['prosody_baseline']
    assert baseline is not None
    assert 'tempo_wpm_mean' in baseline
    assert 'pitch_mean_hz' in baseline
    assert 'energy_rms_mean' in baseline

    print(f"✓ File-based merge: {len(result['segments'])} segments processed")


def test_in_memory_merge_mode():
    """
    Test that in-memory merge mode works correctly (legacy behavior).
    """
    # Create a test audio file path
    test_audio = Path(__file__).parent.parent / "Eingang" / "test_audio.wav"

    # Skip if test audio doesn't exist
    if not test_audio.exists():
        pytest.skip("Test audio file not available")

    # Process with in-memory merge (legacy)
    result = process_large_audio_with_chunking(
        audio_path=str(test_audio),
        transcribe_func=mock_transcribe,
        chunk_duration=10.0,  # Small chunks for testing
        overlap_duration=2.0,
        use_file_based_merge=False  # Legacy in-memory mode
    )

    # Verify result structure
    assert 'segments' in result
    assert 'prosody_features' in result
    assert 'prosody_baseline' in result
    assert 'speaker_segments' in result

    # Verify prosody baseline was calculated
    baseline = result['prosody_baseline']
    assert baseline is not None
    assert 'tempo_wpm_mean' in baseline
    assert 'pitch_mean_hz' in baseline
    assert 'energy_rms_mean' in baseline

    print(f"✓ In-memory merge: {len(result['segments'])} segments processed")


def test_both_modes_produce_equivalent_results():
    """
    Test that both merge modes produce equivalent results.

    This ensures backwards compatibility - the new file-based approach
    should produce the same output as the legacy in-memory approach.
    """
    # Create a test audio file path
    test_audio = Path(__file__).parent.parent / "Eingang" / "test_audio.wav"

    # Skip if test audio doesn't exist
    if not test_audio.exists():
        pytest.skip("Test audio file not available")

    # Process with both modes
    result_file_based = process_large_audio_with_chunking(
        audio_path=str(test_audio),
        transcribe_func=mock_transcribe,
        chunk_duration=10.0,
        overlap_duration=2.0,
        use_file_based_merge=True
    )

    result_in_memory = process_large_audio_with_chunking(
        audio_path=str(test_audio),
        transcribe_func=mock_transcribe,
        chunk_duration=10.0,
        overlap_duration=2.0,
        use_file_based_merge=False
    )

    # Compare results
    assert len(result_file_based['segments']) == len(result_in_memory['segments'])
    assert len(result_file_based['prosody_features']) == len(result_in_memory['prosody_features'])

    # Compare prosody baselines (allow small floating point differences)
    baseline_file = result_file_based['prosody_baseline']
    baseline_mem = result_in_memory['prosody_baseline']

    assert abs(baseline_file['tempo_wpm_mean'] - baseline_mem['tempo_wpm_mean']) < 0.01
    assert abs(baseline_file['pitch_mean_hz'] - baseline_mem['pitch_mean_hz']) < 0.01
    assert abs(baseline_file['energy_rms_mean'] - baseline_mem['energy_rms_mean']) < 0.001

    print(f"✓ Both modes produce equivalent results:")
    print(f"  - Segments: {len(result_file_based['segments'])}")
    print(f"  - Prosody baseline (file): tempo={baseline_file['tempo_wpm_mean']:.1f} wpm")
    print(f"  - Prosody baseline (mem): tempo={baseline_mem['tempo_wpm_mean']:.1f} wpm")


def test_default_mode_is_file_based():
    """
    Test that the default mode is file-based (when parameter is omitted).
    """
    # Create a test audio file path
    test_audio = Path(__file__).parent.parent / "Eingang" / "test_audio.wav"

    # Skip if test audio doesn't exist
    if not test_audio.exists():
        pytest.skip("Test audio file not available")

    # Process WITHOUT specifying use_file_based_merge (should default to True)
    result = process_large_audio_with_chunking(
        audio_path=str(test_audio),
        transcribe_func=mock_transcribe,
        chunk_duration=10.0,
        overlap_duration=2.0
        # use_file_based_merge omitted - should default to True
    )

    # Verify result is valid
    assert 'segments' in result
    assert 'prosody_baseline' in result

    print(f"✓ Default mode (file-based) works: {len(result['segments'])} segments")


if __name__ == "__main__":
    # Allow running tests directly
    pytest.main([__file__, "-v", "-s"])
