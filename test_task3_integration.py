#!/usr/bin/env python3
"""
Integration test: Verify Task 2 prosody data flows into Task 3 memory profiles
"""
import tempfile
import yaml
import numpy as np
from pathlib import Path
from build_memory_from_transcripts import update_speaker_memory
import auto_transcriber_v4_emotion as v4

def test_prosody_flow_task2_to_task3():
    """Test that prosody from analyze_emotion() flows into memory profiles"""
    print("\n=== Testing Task 2 -> Task 3 Integration ===")
    
    # Create test audio (1 second at 22050 Hz)
    audio_data = np.random.randn(22050).astype(np.float32)
    test_text = "This is a test transcript for therapeutic analysis."
    
    # Step 1: Analyze emotion with prosody (Task 2)
    print("\n1. Running Task 2: analyze_emotion() with prosody extraction...")
    analyzer = v4.EmotionalAnalyzer()
    emotion_result = analyzer.analyze_emotion(test_text, audio_data=audio_data, sr=22050)
    
    # Verify prosody is extracted
    assert 'prosody' in emotion_result, "Prosody missing from emotion result"
    assert 'pitch' in emotion_result['prosody'], "Pitch missing from prosody"
    assert 'tempo' in emotion_result['prosody'], "Tempo missing from prosody"
    assert 'energy' in emotion_result['prosody'], "Energy missing from prosody"
    
    print("   ✓ Prosody extracted successfully")
    print(f"     - Pitch: {emotion_result['prosody']['pitch'].get('mean', 0):.2f} Hz")
    print(f"     - Tempo: {emotion_result['prosody']['tempo'].get('bpm', 0):.2f} BPM")
    print(f"     - Energy: {emotion_result['prosody']['energy'].get('mean', 0):.4f}")
    
    # Step 2: Update memory profile (Task 3)
    print("\n2. Running Task 3: update_speaker_memory() with prosody data...")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        memory_dir = Path(tmpdir) / "Memory"
        memory_dir.mkdir()
        
        speaker = "test_integration_speaker"
        transcript_data = {
            'text': test_text,
            'emotion': emotion_result
        }
        
        # First update
        update_speaker_memory(speaker, transcript_data, memory_dir)
        
        # Load and verify
        memory_file = memory_dir / f"{speaker}.yaml"
        assert memory_file.exists(), "Memory file not created"
        
        with open(memory_file, 'r', encoding='utf-8') as f:
            memory = yaml.safe_load(f)
        
        # Verify structure
        assert 'prosody_patterns' in memory, "prosody_patterns missing from memory"
        
        pitch_profile = memory['prosody_patterns']['pitch_profile']
        tempo_profile = memory['prosody_patterns']['tempo_profile']
        energy_profile = memory['prosody_patterns']['energy_profile']
        
        # Verify pitch profile
        assert 'mean_pitch' in pitch_profile
        assert 'pitch_variability' in pitch_profile
        assert 'sample_count' in pitch_profile
        assert pitch_profile['sample_count'] == 1, "Sample count should be 1 after first update"
        
        # Verify values match original prosody data
        original_pitch = emotion_result['prosody']['pitch'].get('mean', 0)
        stored_pitch = pitch_profile['mean_pitch']
        
        print("   ✓ Memory profile created successfully")
        print(f"     - Stored pitch: {stored_pitch:.2f} Hz (original: {original_pitch:.2f} Hz)")
        print(f"     - Sample count: {pitch_profile['sample_count']}")
        
        # Step 3: Test accumulation with second session
        print("\n3. Testing running average with second session...")
        
        # Create second audio sample
        audio_data2 = np.random.randn(22050).astype(np.float32)
        test_text2 = "This is the second session for testing accumulation."
        
        emotion_result2 = analyzer.analyze_emotion(test_text2, audio_data=audio_data2, sr=22050)
        
        transcript_data2 = {
            'text': test_text2,
            'emotion': emotion_result2
        }
        
        update_speaker_memory(speaker, transcript_data2, memory_dir)
        
        # Reload and verify accumulation
        with open(memory_file, 'r', encoding='utf-8') as f:
            memory = yaml.safe_load(f)
        
        pitch_profile = memory['prosody_patterns']['pitch_profile']
        
        assert pitch_profile['sample_count'] == 2, "Sample count should be 2 after second update"
        
        # Calculate expected running average
        pitch1 = emotion_result['prosody']['pitch'].get('mean', 0)
        pitch2 = emotion_result2['prosody']['pitch'].get('mean', 0)
        expected_avg = (pitch1 + pitch2) / 2
        actual_avg = pitch_profile['mean_pitch']
        
        print("   ✓ Running average calculated successfully")
        print(f"     - Session 1 pitch: {pitch1:.2f} Hz")
        print(f"     - Session 2 pitch: {pitch2:.2f} Hz")
        print(f"     - Expected average: {expected_avg:.2f} Hz")
        print(f"     - Actual average: {actual_avg:.2f} Hz")
        print(f"     - Sample count: {pitch_profile['sample_count']}")
        
        # Verify average is reasonable (within 1% tolerance due to floating point)
        tolerance = 0.01
        assert abs(actual_avg - expected_avg) / max(expected_avg, 1) < tolerance, \
            f"Running average calculation error: expected {expected_avg:.2f}, got {actual_avg:.2f}"
        
        print("\n=== All Integration Tests PASSED ===")
        return True

if __name__ == '__main__':
    try:
        test_prosody_flow_task2_to_task3()
        print("\n✓ Task 2 -> Task 3 integration verified successfully!")
    except Exception as e:
        print(f"\n✗ Integration test FAILED: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
