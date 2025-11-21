#!/usr/bin/env python3
"""
Verify the YAML structure matches Task 3 requirements
"""
import tempfile
import yaml
import numpy as np
from pathlib import Path
from build_memory_from_transcripts import update_speaker_memory
import auto_transcriber_v4_emotion as v4

def test_yaml_structure():
    """Test that generated YAML has correct structure for Voice-Marker 2.0"""
    print("\n=== Verifying YAML Structure for Voice-Marker 2.0 ===\n")
    
    # Create test data
    audio_data = np.random.randn(22050).astype(np.float32)
    test_text = "Testing YAML structure for therapeutic transcription."
    
    analyzer = v4.EmotionalAnalyzer()
    emotion_result = analyzer.analyze_emotion(test_text, audio_data=audio_data, sr=22050)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        memory_dir = Path(tmpdir) / "Memory"
        memory_dir.mkdir()
        
        speaker = "structure_test_speaker"
        transcript_data = {
            'text': test_text,
            'emotion': emotion_result
        }
        
        # Create 3 sessions to test accumulation
        for i in range(3):
            audio = np.random.randn(22050).astype(np.float32)
            emotion = analyzer.analyze_emotion(f"Session {i+1} text", audio_data=audio, sr=22050)
            data = {'text': f"Session {i+1} text", 'emotion': emotion}
            update_speaker_memory(speaker, data, memory_dir)
        
        # Load and analyze structure
        memory_file = memory_dir / f"{speaker}.yaml"
        with open(memory_file, 'r', encoding='utf-8') as f:
            memory = yaml.safe_load(f)
        
        print("Generated YAML Structure:")
        print("=" * 60)
        
        # Verify top-level structure
        required_keys = ['name', 'last_updated', 'total_interactions', 'statistics', 
                        'topics', 'characteristics', 'prosody_patterns']
        
        for key in required_keys:
            status = "✓" if key in memory else "✗"
            print(f"{status} {key}: {type(memory.get(key, None)).__name__}")
        
        print("\nprosody_patterns structure:")
        print("-" * 60)
        
        pp = memory['prosody_patterns']
        
        # Verify pitch_profile
        print("\npitch_profile:")
        for field in ['mean_pitch', 'pitch_variability', 'sample_count']:
            value = pp['pitch_profile'].get(field, 'MISSING')
            print(f"  - {field}: {value} ({type(value).__name__})")
        
        # Verify tempo_profile
        print("\ntempo_profile:")
        for field in ['mean_bpm', 'mean_speech_rate', 'sample_count']:
            value = pp['tempo_profile'].get(field, 'MISSING')
            print(f"  - {field}: {value} ({type(value).__name__})")
        
        # Verify energy_profile
        print("\nenergy_profile:")
        for field in ['mean_energy', 'energy_variability', 'mean_dynamic_range', 'sample_count']:
            value = pp['energy_profile'].get(field, 'MISSING')
            print(f"  - {field}: {value} ({type(value).__name__})")
        
        print("\n" + "=" * 60)
        print(f"Total interactions: {memory['total_interactions']}")
        print(f"Sample counts: pitch={pp['pitch_profile']['sample_count']}, "
              f"tempo={pp['tempo_profile']['sample_count']}, "
              f"energy={pp['energy_profile']['sample_count']}")
        
        # Verify all sample counts match
        assert pp['pitch_profile']['sample_count'] == 3
        assert pp['tempo_profile']['sample_count'] == 3
        assert pp['energy_profile']['sample_count'] == 3
        assert memory['total_interactions'] == 3
        
        print("\n✓ All sample counts consistent: 3 sessions recorded")
        
        # Show actual YAML output
        print("\n" + "=" * 60)
        print("Sample YAML Output:")
        print("=" * 60)
        print(yaml.dump(memory, allow_unicode=True, default_flow_style=False))
        
        return True

if __name__ == '__main__':
    try:
        test_yaml_structure()
        print("\n✓ YAML structure verification PASSED!")
    except Exception as e:
        print(f"\n✗ YAML structure verification FAILED: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
