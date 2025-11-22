#!/usr/bin/env python3
"""
Generate synthetic audio files with known ground truth for speaker diarization testing
"""

import json
import numpy as np
import soundfile as sf
from pathlib import Path
from typing import List, Dict, Any


def generate_sine_wave(frequency: float, duration: float, sample_rate: int = 16000) -> np.ndarray:
    """Generate a sine wave at given frequency"""
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    wave = 0.3 * np.sin(2 * np.pi * frequency * t)

    # Add envelope for natural sound
    envelope = np.hanning(len(wave))
    wave *= envelope

    return wave


def add_noise(audio: np.ndarray, snr_db: float) -> np.ndarray:
    """Add Gaussian noise to achieve target SNR"""
    signal_power = np.mean(audio ** 2)
    noise_power = signal_power / (10 ** (snr_db / 10))
    noise = np.sqrt(noise_power) * np.random.randn(len(audio))
    return audio + noise


def generate_test_audio(
    output_path: Path,
    segments: List[Dict[str, Any]],
    total_duration: float,
    sample_rate: int = 16000,
    add_noise_db: float = None
) -> Dict[str, Any]:
    """
    Generate synthetic audio with multiple speakers

    Args:
        output_path: Path to save WAV file
        segments: List of segment dicts with 'start', 'end', 'speaker', 'frequency'
        total_duration: Total audio duration in seconds
        sample_rate: Audio sample rate
        add_noise_db: If set, add noise to achieve this SNR in dB

    Returns:
        Ground truth annotation dict
    """
    # Initialize audio buffer
    audio = np.zeros(int(sample_rate * total_duration))

    # Get unique speakers
    speakers = sorted(set(seg['speaker'] for seg in segments))

    # Generate each segment
    for seg in segments:
        start_sample = int(seg['start'] * sample_rate)
        end_sample = int(seg['end'] * sample_rate)
        duration = seg['end'] - seg['start']

        # Generate sine wave for this segment
        segment_wave = generate_sine_wave(seg['frequency'], duration, sample_rate)

        # Add to audio buffer
        audio[start_sample:end_sample] = segment_wave

    # Add noise if requested
    if add_noise_db is not None:
        audio = add_noise(audio, add_noise_db)

    # Normalize
    audio = audio / np.max(np.abs(audio)) if np.max(np.abs(audio)) > 0 else audio

    # Save audio
    sf.write(str(output_path), audio, sample_rate)

    # Create ground truth annotation
    ground_truth = {
        'audio_file': output_path.name,
        'duration': total_duration,
        'sample_rate': sample_rate,
        'num_speakers': len(speakers),
        'speakers': speakers,
        'segments': [
            {
                'start': seg['start'],
                'end': seg['end'],
                'speaker': seg['speaker'],
                'duration': seg['end'] - seg['start']
            }
            for seg in segments
        ],
        'metadata': {
            'synthetic': True,
            'noise_level_db': add_noise_db,
            'generation_method': 'sine_wave'
        }
    }

    return ground_truth


def main():
    """Generate all ground truth test files"""

    output_dir = Path(__file__).parent / "ground_truth"
    output_dir.mkdir(exist_ok=True)

    print("Generating ground truth test files...")
    print(f"Output directory: {output_dir}")

    # =========================================================================
    # Test 1: 2 Speakers, Clear, No Overlap
    # =========================================================================
    print("\n1. Generating test_2speakers_clear.wav...")

    test1_segments = [
        {'start': 0.0, 'end': 5.0, 'speaker': 'Speaker A', 'frequency': 200},
        {'start': 5.5, 'end': 10.0, 'speaker': 'Speaker B', 'frequency': 400},
        {'start': 10.5, 'end': 15.0, 'speaker': 'Speaker A', 'frequency': 200},
        {'start': 15.5, 'end': 20.0, 'speaker': 'Speaker B', 'frequency': 400},
        {'start': 20.5, 'end': 25.0, 'speaker': 'Speaker A', 'frequency': 200},
    ]

    gt1 = generate_test_audio(
        output_dir / "test_2speakers_clear.wav",
        test1_segments,
        total_duration=30.0,
        add_noise_db=None  # Clean
    )

    with open(output_dir / "test_2speakers_clear.json", 'w') as f:
        json.dump(gt1, f, indent=2)

    print(f"   ✓ Created: {gt1['audio_file']}")
    print(f"   ✓ Duration: {gt1['duration']}s, Speakers: {gt1['num_speakers']}, Segments: {len(gt1['segments'])}")

    # =========================================================================
    # Test 2: 2 Speakers, With Overlaps
    # =========================================================================
    print("\n2. Generating test_2speakers_overlap.wav...")

    test2_segments = [
        {'start': 0.0, 'end': 5.0, 'speaker': 'Speaker A', 'frequency': 200},
        {'start': 4.5, 'end': 9.0, 'speaker': 'Speaker B', 'frequency': 400},  # Overlap!
        {'start': 9.5, 'end': 14.0, 'speaker': 'Speaker A', 'frequency': 200},
        {'start': 13.5, 'end': 18.0, 'speaker': 'Speaker B', 'frequency': 400},  # Overlap!
        {'start': 18.5, 'end': 23.0, 'speaker': 'Speaker A', 'frequency': 200},
    ]

    gt2 = generate_test_audio(
        output_dir / "test_2speakers_overlap.wav",
        test2_segments,
        total_duration=30.0,
        add_noise_db=None
    )

    # Mark overlaps in ground truth
    gt2['overlaps'] = [
        {'start': 4.5, 'end': 5.0, 'speakers': ['Speaker A', 'Speaker B']},
        {'start': 13.5, 'end': 14.0, 'speakers': ['Speaker A', 'Speaker B']},
    ]

    with open(output_dir / "test_2speakers_overlap.json", 'w') as f:
        json.dump(gt2, f, indent=2)

    print(f"   ✓ Created: {gt2['audio_file']}")
    print(f"   ✓ Overlaps: {len(gt2['overlaps'])}")

    # =========================================================================
    # Test 3: 3 Speakers, Clear
    # =========================================================================
    print("\n3. Generating test_3speakers_clear.wav...")

    test3_segments = [
        {'start': 0.0, 'end': 4.0, 'speaker': 'Speaker A', 'frequency': 200},
        {'start': 4.5, 'end': 8.5, 'speaker': 'Speaker B', 'frequency': 400},
        {'start': 9.0, 'end': 13.0, 'speaker': 'Speaker C', 'frequency': 300},
        {'start': 13.5, 'end': 17.5, 'speaker': 'Speaker A', 'frequency': 200},
        {'start': 18.0, 'end': 22.0, 'speaker': 'Speaker B', 'frequency': 400},
        {'start': 22.5, 'end': 26.5, 'speaker': 'Speaker C', 'frequency': 300},
    ]

    gt3 = generate_test_audio(
        output_dir / "test_3speakers_clear.wav",
        test3_segments,
        total_duration=30.0,
        add_noise_db=None
    )

    with open(output_dir / "test_3speakers_clear.json", 'w') as f:
        json.dump(gt3, f, indent=2)

    print(f"   ✓ Created: {gt3['audio_file']}")
    print(f"   ✓ Speakers: {gt3['num_speakers']}, Segments: {len(gt3['segments'])}")

    # =========================================================================
    # Test 4: 2 Speakers, Noisy (Low SNR)
    # =========================================================================
    print("\n4. Generating test_2speakers_noisy.wav...")

    test4_segments = [
        {'start': 0.0, 'end': 5.0, 'speaker': 'Speaker A', 'frequency': 200},
        {'start': 5.5, 'end': 10.0, 'speaker': 'Speaker B', 'frequency': 400},
        {'start': 10.5, 'end': 15.0, 'speaker': 'Speaker A', 'frequency': 200},
        {'start': 15.5, 'end': 20.0, 'speaker': 'Speaker B', 'frequency': 400},
    ]

    gt4 = generate_test_audio(
        output_dir / "test_2speakers_noisy.wav",
        test4_segments,
        total_duration=25.0,
        add_noise_db=10.0  # 10dB SNR (noisy)
    )

    with open(output_dir / "test_2speakers_noisy.json", 'w') as f:
        json.dump(gt4, f, indent=2)

    print(f"   ✓ Created: {gt4['audio_file']}")
    print(f"   ✓ SNR: {gt4['metadata']['noise_level_db']}dB")

    # =========================================================================
    # Test 5: Single Speaker (Edge Case)
    # =========================================================================
    print("\n5. Generating test_single_speaker.wav...")

    test5_segments = [
        {'start': 0.0, 'end': 4.0, 'speaker': 'Speaker A', 'frequency': 200},
        {'start': 4.5, 'end': 8.5, 'speaker': 'Speaker A', 'frequency': 200},
        {'start': 9.0, 'end': 13.0, 'speaker': 'Speaker A', 'frequency': 200},
        {'start': 13.5, 'end': 17.5, 'speaker': 'Speaker A', 'frequency': 200},
    ]

    gt5 = generate_test_audio(
        output_dir / "test_single_speaker.wav",
        test5_segments,
        total_duration=20.0,
        add_noise_db=None
    )

    with open(output_dir / "test_single_speaker.json", 'w') as f:
        json.dump(gt5, f, indent=2)

    print(f"   ✓ Created: {gt5['audio_file']}")
    print(f"   ✓ Speakers: {gt5['num_speakers']}, Segments: {len(gt5['segments'])}")

    # =========================================================================
    # Summary
    # =========================================================================
    print("\n" + "=" * 80)
    print("✅ Ground Truth Test Set Generation Complete")
    print("=" * 80)
    print(f"\nGenerated files:")
    print("  1. test_2speakers_clear.wav      - 2 speakers, clear, no overlap")
    print("  2. test_2speakers_overlap.wav    - 2 speakers, with overlaps")
    print("  3. test_3speakers_clear.wav      - 3 speakers, clear")
    print("  4. test_2speakers_noisy.wav      - 2 speakers, 10dB SNR")
    print("  5. test_single_speaker.wav       - 1 speaker (edge case)")
    print(f"\nOutput directory: {output_dir}")
    print(f"\nNext step: Run evaluation tests with these files")
    print("=" * 80)


if __name__ == "__main__":
    main()
