#!/usr/bin/env python3
import yaml
from pathlib import Path
import tempfile
import shutil

def test_memory_profile_includes_prosody_section():
    """Test that memory profiles have prosody_patterns section"""
    # This will test the enhanced memory structure
    from build_memory_from_transcripts import update_speaker_memory

    with tempfile.TemporaryDirectory() as tmpdir:
        memory_dir = Path(tmpdir) / "Memory"
        memory_dir.mkdir()

        speaker = "test_speaker"
        transcript_data = {
            'text': 'This is a test transcript',
            'emotion': {
                'prosody': {
                    'pitch': {'mean': 150.5, 'std': 20.3},
                    'tempo': {'bpm': 120, 'speech_rate': 4.5},
                    'energy': {'mean': 0.5, 'std': 0.1, 'dynamic_range': 0.3}
                }
            }
        }

        update_speaker_memory(speaker, transcript_data, memory_dir)

        # Load and verify
        memory_file = memory_dir / f"{speaker}.yaml"
        assert memory_file.exists()

        with open(memory_file, 'r', encoding='utf-8') as f:
            memory = yaml.safe_load(f)

        assert 'prosody_patterns' in memory
        assert 'pitch_profile' in memory['prosody_patterns']
        assert 'tempo_profile' in memory['prosody_patterns']
        assert 'energy_profile' in memory['prosody_patterns']

def test_prosody_patterns_accumulate():
    """Test that prosody patterns accumulate over multiple updates"""
    from build_memory_from_transcripts import update_speaker_memory
    print("  Running test_prosody_patterns_accumulate...")

    with tempfile.TemporaryDirectory() as tmpdir:
        memory_dir = Path(tmpdir) / "Memory"
        memory_dir.mkdir()

        speaker = "test_speaker"

        # First transcript
        transcript1 = {
            'text': 'First transcript',
            'emotion': {
                'prosody': {
                    'pitch': {'mean': 150.0, 'std': 20.0},
                    'tempo': {'bpm': 120, 'speech_rate': 4.0},
                    'energy': {'mean': 0.5, 'std': 0.1, 'dynamic_range': 0.3}
                }
            }
        }

        # Second transcript
        transcript2 = {
            'text': 'Second transcript',
            'emotion': {
                'prosody': {
                    'pitch': {'mean': 160.0, 'std': 25.0},
                    'tempo': {'bpm': 130, 'speech_rate': 5.0},
                    'energy': {'mean': 0.6, 'std': 0.15, 'dynamic_range': 0.4}
                }
            }
        }

        update_speaker_memory(speaker, transcript1, memory_dir)
        update_speaker_memory(speaker, transcript2, memory_dir)

        # Verify accumulation
        memory_file = memory_dir / f"{speaker}.yaml"
        with open(memory_file, 'r', encoding='utf-8') as f:
            memory = yaml.safe_load(f)

        # Should have averaged prosody data
        pitch_profile = memory['prosody_patterns']['pitch_profile']
        assert 'mean_pitch' in pitch_profile
        assert pitch_profile['sample_count'] == 2

if __name__ == '__main__':
    print("Testing Memory Prosody Integration...")
    print("\nTest 1: Memory profile includes prosody section")
    try:
        test_memory_profile_includes_prosody_section()
        print("✓ PASSED")
    except Exception as e:
        print(f"✗ FAILED: {e}")

    print("\nTest 2: Prosody patterns accumulate")
    try:
        test_prosody_patterns_accumulate()
        print("✓ PASSED")
    except Exception as e:
        print(f"✗ FAILED: {e}")

    print("\nAll tests complete.")
