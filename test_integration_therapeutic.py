#!/usr/bin/env python3
"""
Integration tests for complete therapeutic transcription pipeline
"""
from pathlib import Path
import tempfile
import shutil
import numpy as np
import yaml
import soundfile as sf


def create_test_audio(output_path: Path, duration: float = 2.0, sr: int = 22050):
    """Create a test audio file"""
    # Generate simple sine wave
    t = np.linspace(0, duration, int(sr * duration))
    audio = np.sin(2 * np.pi * 440 * t) * 0.3  # 440 Hz sine wave

    sf.write(output_path, audio, sr)


def test_full_pipeline_with_prosody():
    """Test complete pipeline: audio -> transcription -> emotion -> prosody -> memory"""

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        # Setup directories
        input_dir = tmpdir / "Eingang" / "test_speaker"
        output_dir = tmpdir / "Transkripte_LLM"
        memory_dir = tmpdir / "Memory"

        input_dir.mkdir(parents=True)
        output_dir.mkdir(parents=True)
        memory_dir.mkdir(parents=True)

        # Create test audio
        audio_file = input_dir / "test_audio.wav"
        create_test_audio(audio_file)

        # Process with V4
        import auto_transcriber_v4_emotion as v4

        # Transcribe
        result = v4.transcribe_with_whisper(str(audio_file), model_size='tiny')

        assert 'text' in result
        assert 'confidence_scores' in result

        # Analyze emotion
        analyzer = v4.EmotionalAnalyzer()
        emotion_data = analyzer.analyze_emotion(
            result['text'],
            audio_path=str(audio_file)
        )

        assert 'emotion' in emotion_data
        assert 'prosody' in emotion_data
        assert 'pitch' in emotion_data['prosody']
        assert 'tempo' in emotion_data['prosody']
        assert 'energy' in emotion_data['prosody']

        # Update memory
        from build_memory_from_transcripts import update_speaker_memory

        update_speaker_memory(
            "test_speaker",
            {'text': result['text'], 'emotion': emotion_data},
            memory_dir
        )

        # Verify memory file
        memory_file = memory_dir / "test_speaker.yaml"
        assert memory_file.exists()

        with open(memory_file, 'r', encoding='utf-8') as f:
            memory = yaml.safe_load(f)

        assert 'prosody_patterns' in memory
        assert memory['prosody_patterns']['pitch_profile']['sample_count'] == 1
        assert memory['prosody_patterns']['tempo_profile']['sample_count'] == 1
        assert memory['prosody_patterns']['energy_profile']['sample_count'] == 1

        print("✓ Full pipeline test passed")


def test_confidence_marking_in_output():
    """Test that low confidence segments are properly marked in output"""

    import auto_transcriber_v4_emotion as v4

    # Mock result with low confidence
    result = {
        'text': 'This is a test with unclear parts',
        'confidence_scores': {
            'overall_confidence': 0.65,
            'segments': [
                {'text': 'This is a test', 'confidence': 0.85, 'start': 0.0, 'end': 1.0},
                {'text': 'with unclear parts', 'confidence': 0.35, 'start': 1.0, 'end': 2.0}
            ],
            'low_confidence_segments': [
                {'text': 'with unclear parts', 'confidence': 0.35, 'start': 1.0, 'end': 2.0}
            ],
            'low_confidence_threshold': 0.5
        }
    }

    marked_text = v4.mark_low_confidence_segments(result)

    assert '[UNSICHER' in marked_text
    assert '0.35' in marked_text

    print("✓ Confidence marking test passed")


if __name__ == "__main__":
    print("=" * 80)
    print("Running Integration Tests for Therapeutic Transcription Pipeline")
    print("=" * 80)

    tests = [
        ("Full Pipeline Test", test_full_pipeline_with_prosody),
        ("Confidence Marking Test", test_confidence_marking_in_output)
    ]

    passed = 0
    failed = 0

    for test_name, test_func in tests:
        print(f"\n[TEST] {test_name}")
        try:
            test_func()
            passed += 1
            print(f"[PASS] {test_name}")
        except Exception as e:
            failed += 1
            print(f"[FAIL] {test_name}")
            print(f"  Error: {e}")
            import traceback
            traceback.print_exc()

    print("\n" + "=" * 80)
    print(f"Test Results: {passed} passed, {failed} failed out of {len(tests)} total")
    print("=" * 80)

    exit(0 if failed == 0 else 1)
