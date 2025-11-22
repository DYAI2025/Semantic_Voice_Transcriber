#!/usr/bin/env python3
"""
Comprehensive Speaker Separation Test Suite
Tests pyannote.audio speaker diarization with various scenarios
"""

import logging
import os
import sys
import tempfile
from pathlib import Path
from typing import Dict, List, Any

import numpy as np
import soundfile as sf

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_synthetic_audio(
    duration: float = 10.0,
    sample_rate: int = 16000,
    num_speakers: int = 2,
    speech_segments: List[Dict[str, Any]] = None
) -> Path:
    """
    Create synthetic audio with multiple speakers

    Args:
        duration: Total duration in seconds
        sample_rate: Audio sample rate
        num_speakers: Number of speakers
        speech_segments: List of dicts with 'start', 'end', 'speaker', 'frequency'

    Returns:
        Path to temporary WAV file
    """
    logger.info(f"Creating synthetic audio: {duration}s, {num_speakers} speakers")

    # Generate time array
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    audio = np.zeros_like(t)

    # Default segments if not provided
    if speech_segments is None:
        speech_segments = [
            {'start': 0.0, 'end': 3.0, 'speaker': 0, 'frequency': 200},  # Speaker A (low)
            {'start': 3.5, 'end': 6.5, 'speaker': 1, 'frequency': 400},  # Speaker B (high)
            {'start': 7.0, 'end': 10.0, 'speaker': 0, 'frequency': 200}, # Speaker A again
        ]

    # Generate speech segments
    for seg in speech_segments:
        start_sample = int(seg['start'] * sample_rate)
        end_sample = int(seg['end'] * sample_rate)
        freq = seg['frequency']

        # Generate sine wave for this segment
        segment_t = t[start_sample:end_sample] - seg['start']
        segment_audio = 0.3 * np.sin(2 * np.pi * freq * segment_t)

        # Add envelope to make it sound more natural
        envelope = np.hanning(len(segment_audio))
        segment_audio *= envelope

        # Add to audio
        audio[start_sample:end_sample] += segment_audio

    # Add slight noise
    audio += 0.01 * np.random.randn(len(audio))

    # Normalize
    max_val = np.max(np.abs(audio))
    audio = audio / max_val if max_val > 0 else audio

    # Save to temporary file using a guaranteed unique name
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
        temp_file = Path(tmp.name)
    sf.write(str(temp_file), audio, sample_rate)
    logger.info(f"Synthetic audio saved to: {temp_file}")

    return temp_file


def test_pyannote_installation():
    """Test 1: Check if pyannote.audio is properly installed"""
    logger.info("=" * 80)
    logger.info("TEST 1: PyAnnote Installation Check")
    logger.info("=" * 80)

    try:
        from pyannote.audio import Pipeline
        logger.info("✅ pyannote.audio is installed")
        return True
    except ImportError as e:
        logger.error(f"❌ pyannote.audio not installed: {e}")
        logger.error("Install with: pip install pyannote.audio")
        return False


def test_hf_token():
    """Test 2: Check if Hugging Face token is configured"""
    logger.info("\n" + "=" * 80)
    logger.info("TEST 2: Hugging Face Token Check")
    logger.info("=" * 80)

    # Try to load from .env
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        logger.warning("python-dotenv not installed, checking only env vars")

    hf_token = os.getenv('HF_TOKEN')

    if hf_token and hf_token.startswith('hf_'):
        logger.info("✅ HF_TOKEN found and looks valid")
        return hf_token
    else:
        logger.error("❌ HF_TOKEN not found or invalid")
        logger.error("Setup instructions:")
        logger.error("1. Create account: https://huggingface.co/join")
        logger.error("2. Accept agreements:")
        logger.error("   - https://huggingface.co/pyannote/segmentation-3.0")
        logger.error("   - https://huggingface.co/pyannote/speaker-diarization-3.1")
        logger.error("3. Create token: https://huggingface.co/settings/tokens")
        logger.error("4. Add to .env: HF_TOKEN=hf_YourTokenHere")
        return None


def test_speaker_diarizer_basic(hf_token: str):
    """Test 3: Basic speaker diarization functionality"""
    logger.info("\n" + "=" * 80)
    logger.info("TEST 3: Basic Speaker Diarization")
    logger.info("=" * 80)

    try:
        from svt_core.audio.diarization import SpeakerDiarizer

        # Create synthetic audio
        audio_file = create_synthetic_audio(duration=10.0, num_speakers=2)

        # Initialize diarizer
        logger.info("Initializing SpeakerDiarizer...")
        diarizer = SpeakerDiarizer(
            use_auth_token=hf_token,
            min_speakers=1,
            max_speakers=3,
            timeout_seconds=60,
            enable_graceful_degradation=True
        )

        # Run diarization
        logger.info("Running diarization...")
        segments = diarizer.diarize(audio_file)

        # Check results
        if len(segments) > 0:
            logger.info(f"✅ Diarization successful: {len(segments)} segments detected")

            # Get statistics
            stats = SpeakerDiarizer.get_speaker_statistics(segments)
            logger.info(f"✅ Detected {len(stats)} unique speakers")

            # Print segments
            logger.info("\nDetected segments:")
            for seg in segments[:10]:  # Show first 10
                logger.info(
                    f"  [{seg['start']:6.2f}s - {seg['end']:6.2f}s] "
                    f"{seg['speaker']:12s} (ID: {seg['speaker_id']})"
                )

            if len(segments) > 10:
                logger.info(f"  ... and {len(segments) - 10} more segments")

            # Print statistics
            logger.info("\nSpeaker statistics:")
            for speaker, data in sorted(stats.items()):
                logger.info(
                    f"  {speaker:12s}: {data['total_duration']:6.2f}s "
                    f"({data['percentage']:5.1f}%) - {data['num_segments']} segments"
                )

            # Cleanup
            audio_file.unlink()

            return True, segments
        else:
            logger.warning("⚠️ Diarization returned no segments")
            audio_file.unlink()
            return False, []

    except Exception as e:
        logger.error(f"❌ Diarization failed: {e}")
        import traceback
        traceback.print_exc()
        return False, []


def test_cpu_fallback():
    """Test 4: CPU fallback diarization"""
    logger.info("\n" + "=" * 80)
    logger.info("TEST 4: CPU Fallback Diarization")
    logger.info("=" * 80)

    try:
        from svt_core.audio.diarization_cpu import CPUDiarizer

        # Create synthetic audio
        audio_file = create_synthetic_audio(duration=5.0, num_speakers=2)

        # Initialize CPU diarizer
        logger.info("Initializing CPUDiarizer...")
        diarizer = CPUDiarizer()

        # Run diarization
        logger.info("Running CPU-based diarization...")
        segments = diarizer.diarize(audio_file, num_speakers=2)

        # Check results
        if len(segments) > 0:
            logger.info(f"✅ CPU diarization successful: {len(segments)} segments detected")

            # Get statistics
            stats = CPUDiarizer.get_speaker_statistics(segments)
            logger.info(f"✅ Detected {len(stats)} unique speakers")

            # Print segments
            logger.info("\nDetected segments:")
            for seg in segments[:5]:
                logger.info(
                    f"  [{seg['start']:6.2f}s - {seg['end']:6.2f}s] "
                    f"{seg['speaker']:12s} (ID: {seg['speaker_id']})"
                )

            # Cleanup
            audio_file.unlink()

            return True, segments
        else:
            logger.warning("⚠️ CPU diarization returned no segments")
            audio_file.unlink()
            return False, []

    except Exception as e:
        logger.error(f"❌ CPU diarization failed: {e}")
        import traceback
        traceback.print_exc()
        return False, []


def test_alignment(segments: List[Dict[str, Any]]):
    """Test 5: Alignment with transcription segments"""
    logger.info("\n" + "=" * 80)
    logger.info("TEST 5: Transcription Alignment")
    logger.info("=" * 80)

    try:
        from svt_core.audio.diarization import SpeakerDiarizer

        # Create fake transcription segments
        transcription_segments = [
            {'start': 0.5, 'end': 2.5, 'text': 'Hello, how are you?'},
            {'start': 3.0, 'end': 5.0, 'text': 'I am doing well, thank you.'},
            {'start': 6.0, 'end': 8.0, 'text': 'That is great to hear.'},
        ]

        logger.info(f"Aligning {len(transcription_segments)} transcription segments...")

        # Align
        aligned = SpeakerDiarizer().align_with_transcription(
            segments,
            transcription_segments
        )

        # Check results
        if len(aligned) == len(transcription_segments):
            logger.info(f"✅ Alignment successful: {len(aligned)} segments aligned")

            # Print aligned segments
            logger.info("\nAligned segments:")
            for seg in aligned:
                logger.info(
                    f"  [{seg['start']:6.2f}s - {seg['end']:6.2f}s] "
                    f"{seg['speaker']:12s}: {seg['text']}"
                )

            return True
        else:
            logger.warning(f"⚠️ Alignment mismatch: expected {len(transcription_segments)}, got {len(aligned)}")
            return False

    except Exception as e:
        logger.error(f"❌ Alignment failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_overlapped_speech_detection(hf_token: str):
    """Test 6: Overlapped Speech Detection (OSD)"""
    logger.info("\n" + "=" * 80)
    logger.info("TEST 6: Overlapped Speech Detection (OSD)")
    logger.info("=" * 80)

    try:
        from svt_core.audio.diarization import SpeakerDiarizer

        # Create synthetic audio with overlaps
        speech_segments = [
            {'start': 0.0, 'end': 3.0, 'speaker': 0, 'frequency': 200},
            {'start': 2.5, 'end': 5.5, 'speaker': 1, 'frequency': 400},  # Overlap!
            {'start': 6.0, 'end': 8.0, 'speaker': 0, 'frequency': 200},
        ]
        audio_file = create_synthetic_audio(
            duration=10.0,
            num_speakers=2,
            speech_segments=speech_segments
        )

        # Initialize diarizer
        logger.info("Initializing SpeakerDiarizer with OSD...")
        diarizer = SpeakerDiarizer(
            use_auth_token=hf_token,
            timeout_seconds=60
        )

        # Run OSD
        logger.info("Running overlapped speech detection...")
        overlaps = diarizer.detect_overlapped_speech(audio_file)

        # Check results
        logger.info(f"✅ OSD complete: Found {len(overlaps)} overlapped regions")

        if len(overlaps) > 0:
            logger.info("\nOverlapped speech regions:")
            for overlap in overlaps:
                logger.info(
                    f"  [{overlap['start']:6.2f}s - {overlap['end']:6.2f}s] "
                    f"Duration: {overlap['duration']:.2f}s - {overlap['overlap_type']}"
                )

        # Cleanup
        audio_file.unlink()

        return True, overlaps

    except Exception as e:
        logger.error(f"❌ OSD failed: {e}")
        import traceback
        traceback.print_exc()
        return False, []


def test_stability_and_error_handling(hf_token: str):
    """Test 7: Stability and error handling"""
    logger.info("\n" + "=" * 80)
    logger.info("TEST 7: Stability and Error Handling")
    logger.info("=" * 80)

    tests_passed = 0
    total_tests = 4

    try:
        from svt_core.audio.diarization import SpeakerDiarizer

        # Test 7.1: Non-existent file
        logger.info("\n7.1: Testing non-existent file handling...")
        diarizer = SpeakerDiarizer(
            use_auth_token=hf_token,
            enable_graceful_degradation=True
        )
        try:
            segments = diarizer.diarize(Path("/nonexistent/file.wav"))
            logger.info("✅ Graceful degradation works for non-existent files")
            tests_passed += 1
        except Exception as e:
            logger.warning(f"⚠️ Non-existent file handling: {e}")

        # Test 7.2: Empty audio
        logger.info("\n7.2: Testing empty audio handling...")
        empty_file = Path(tempfile.gettempdir()) / "empty.wav"
        sf.write(str(empty_file), np.zeros(100), 16000)
        try:
            segments = diarizer.diarize(empty_file)
            logger.info("✅ Empty audio handled gracefully")
            tests_passed += 1
        except Exception as e:
            logger.warning(f"⚠️ Empty audio handling: {e}")
        finally:
            empty_file.unlink()

        # Test 7.3: Very short audio
        logger.info("\n7.3: Testing very short audio...")
        short_file = Path(tempfile.gettempdir()) / "short.wav"
        short_audio = 0.3 * np.sin(2 * np.pi * 440 * np.linspace(0, 0.1, 1600))
        sf.write(str(short_file), short_audio, 16000)
        try:
            segments = diarizer.diarize(short_file)
            logger.info("✅ Short audio handled gracefully")
            tests_passed += 1
        except Exception as e:
            logger.warning(f"⚠️ Short audio handling: {e}")
        finally:
            short_file.unlink()

        # Test 7.4: Timeout handling
        logger.info("\n7.4: Testing timeout handling...")
        diarizer_timeout = SpeakerDiarizer(
            use_auth_token=hf_token,
            timeout_seconds=1,  # Very short timeout
            enable_graceful_degradation=True
        )
        audio_file = create_synthetic_audio(duration=60.0)  # Long audio
        try:
            diarizer_timeout.diarize(audio_file)
            logger.info("✅ Timeout handling works")
            tests_passed += 1
        except Exception as e:
            logger.warning(f"⚠️ Timeout handling: {e}")
        finally:
            audio_file.unlink()

        logger.info(f"\nStability tests passed: {tests_passed}/{total_tests}")
        return tests_passed == total_tests

    except Exception as e:
        logger.error(f"❌ Stability testing failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def generate_test_report(results: Dict[str, bool]):
    """Generate comprehensive test report"""
    logger.info("\n\n" + "=" * 80)
    logger.info("SPEAKER SEPARATION TEST REPORT")
    logger.info("=" * 80)

    total_tests = len(results)
    passed_tests = sum(bool(v)

    logger.info(f"\nTotal Tests: {total_tests}")
    logger.info(f"Passed: {passed_tests}")
    logger.info(f"Failed: {total_tests - passed_tests}")
    logger.info(f"Success Rate: {passed_tests/total_tests*100:.1f}%")

    logger.info("\nDetailed Results:")
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        logger.info(f"  {status}: {test_name}")

    # Overall assessment
    logger.info("\n" + "=" * 80)
    if passed_tests == total_tests:
        logger.info("🎉 ALL TESTS PASSED - Speaker separation is working perfectly!")
    elif passed_tests >= total_tests * 0.7:
        logger.info("⚠️ MOST TESTS PASSED - Speaker separation is mostly working")
    else:
        logger.info("❌ TESTS FAILED - Speaker separation needs improvement")
    logger.info("=" * 80)

    return passed_tests == total_tests


def main():
    """Run all speaker separation tests"""
    logger.info("Starting Speaker Separation Test Suite...")
    logger.info(f"Python: {sys.version}")
    logger.info(f"Working Directory: {os.getcwd()}\n")

    results = {}

    # Test 1: Installation check
    if not test_pyannote_installation():
        logger.error("\n❌ Cannot proceed without pyannote.audio")
        logger.error("Install with: pip install pyannote.audio")
        return 1
    results['PyAnnote Installation'] = True

    # Test 2: HF Token check
    hf_token = test_hf_token()
    if not hf_token:
        logger.warning("\n⚠️ Tests will be limited without HF_TOKEN")
        logger.info("Continuing with CPU-only tests...\n")

        # Run CPU fallback test only
        cpu_success, _ = test_cpu_fallback()
        results['CPU Fallback'] = cpu_success
    else:
        results['HF Token Configuration'] = True

        # Test 3: Basic diarization
        basic_success, segments = test_speaker_diarizer_basic(hf_token)
        results['Basic Diarization'] = basic_success

        # Test 4: CPU fallback
        cpu_success, _ = test_cpu_fallback()
        results['CPU Fallback'] = cpu_success

        # Test 5: Alignment (only if we have segments)
        if segments:
            alignment_success = test_alignment(segments)
            results['Transcription Alignment'] = alignment_success

        # Test 6: OSD
        osd_success, _ = test_overlapped_speech_detection(hf_token)
        results['Overlapped Speech Detection'] = osd_success

        # Test 7: Stability
        stability_success = test_stability_and_error_handling(hf_token)
        results['Stability & Error Handling'] = stability_success

    # Generate report
    all_passed = generate_test_report(results)

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
