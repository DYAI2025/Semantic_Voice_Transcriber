#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Prosody Pipeline - Quick test of complete Phase 1 implementation

Tests the complete flow:
1. Audio quality analysis
2. Whisper transcription
3. Prosody extraction (Big 4)
4. Baseline calculation
5. Annotated Markdown + JSON output
"""

import sys
from pathlib import Path
import librosa
import soundfile as sf
import tempfile
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import our modules
from audio_quality_analyzer import AudioQualityAnalyzer
from audio_preprocessor import AudioPreprocessor
import auto_transcriber_v4_emotion as v4
from output_formatter import OutputFormatter


def test_complete_pipeline(audio_file: str, duration_seconds: int = 30):
    """
    Test complete prosody pipeline on a short audio clip

    Args:
        audio_file: Path to audio file
        duration_seconds: How many seconds to test (default 30s for quick test)
    """

    logger.info("=" * 60)
    logger.info("🧪 Testing Complete Prosody Pipeline (Phase 1)")
    logger.info("=" * 60)

    # Check if file exists
    audio_path = Path(audio_file)
    if not audio_path.exists():
        logger.error(f"❌ Audio file not found: {audio_file}")
        return False

    logger.info(f"\n📁 Audio file: {audio_path.name}")
    logger.info(f"   Size: {audio_path.stat().st_size / 1024 / 1024:.1f} MB")

    # Extract first N seconds for testing
    logger.info(f"\n⏱️  Extracting first {duration_seconds} seconds for quick test...")
    try:
        audio, sr = librosa.load(str(audio_path), sr=16000, duration=duration_seconds)

        # Save to temp file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
            tmp_path = tmp_file.name
            sf.write(tmp_path, audio, sr)
            logger.info(f"   Saved test clip to: {tmp_path}")

    except Exception as e:
        logger.error(f"❌ Failed to extract audio clip: {e}")
        return False

    # Step 1: Quality Analysis
    logger.info(f"\n🔍 STEP 1: Analyzing audio quality...")
    quality_analyzer = AudioQualityAnalyzer()
    quality_metrics = quality_analyzer.analyze_audio_file(tmp_path)

    logger.info(f"   Quality Score: {quality_metrics['quality_score']:.2f}")
    logger.info(f"   SNR: {quality_metrics['snr_db']:.1f} dB")
    logger.info(f"   Clipping: {quality_metrics['clipping_ratio']:.1%}")
    logger.info(f"   Silence: {quality_metrics['silence_ratio']:.1%}")

    # Step 2: Transcription with Prosody
    logger.info(f"\n🎤 STEP 2: Transcribing with Whisper + Prosody extraction...")

    result = v4.transcribe_with_whisper(
        tmp_path,
        model_size='small',  # Use small model for speed
        language='de',
        use_intelligent_pipeline=False,  # Skip preprocessing for test
        extract_prosody=True  # Enable prosody extraction
    )

    logger.info(f"   ✅ Transcription complete!")
    logger.info(f"   Text length: {len(result['text'])} characters")
    logger.info(f"   Segments: {len(result.get('segments', []))}")
    logger.info(f"   Overall confidence: {result['confidence_scores']['overall_confidence']:.2%}")

    # Check prosody results
    prosody_features = result.get('prosody_features', [])
    prosody_baseline = result.get('prosody_baseline', None)

    if prosody_features:
        logger.info(f"\n🎵 STEP 3: Prosody extraction results")
        logger.info(f"   Segments with prosody: {len(prosody_features)}")

        if prosody_baseline:
            logger.info(f"\n   📊 Baseline:")
            logger.info(f"      Tempo: {prosody_baseline['tempo_wpm_mean']:.1f} WPM")
            logger.info(f"      Pitch: {prosody_baseline['pitch_mean_hz']:.1f} Hz")
            logger.info(f"      Energy: {prosody_baseline['energy_rms_mean']:.4f}")

        # Show first segment details
        if len(prosody_features) > 0:
            first = prosody_features[0]
            logger.info(f"\n   🔬 First Segment Example:")
            logger.info(f"      Time: {first['start_time']:.1f}s - {first['end_time']:.1f}s")
            logger.info(f"      Tempo: {first.get('tempo_wpm', 0):.1f} WPM ({first.get('tempo_deviation_pct', 0):+.1f}%)")
            logger.info(f"      Pitch: {first.get('pitch_mean_hz', 0):.1f} Hz ({first.get('pitch_deviation_pct', 0):+.1f}%)")
            logger.info(f"      Energy: {first.get('energy_rms', 0):.4f} ({first.get('energy_deviation_pct', 0):+.1f}%)")

    else:
        logger.warning(f"   ⚠️ No prosody features extracted!")

    # Step 4: Generate outputs
    logger.info(f"\n📝 STEP 4: Generating annotated outputs...")

    formatter = OutputFormatter()
    output_base = Path("Transkripte_LLM") / f"test_{audio_path.stem}"
    output_base.parent.mkdir(exist_ok=True)

    try:
        files = formatter.format_transcript(
            result,
            audio_path.name,
            output_base,
            include_prosody_markers=True
        )

        logger.info(f"   ✅ Generated outputs:")
        logger.info(f"      Markdown: {files['markdown']}")
        logger.info(f"      JSON: {files['json']}")

        # Show preview of markdown
        logger.info(f"\n📄 Markdown Preview (first 500 chars):")
        logger.info("-" * 60)
        with open(files['markdown'], 'r', encoding='utf-8') as f:
            content = f.read()
            logger.info(content[:500] + "...")
        logger.info("-" * 60)

    except Exception as e:
        logger.error(f"   ❌ Failed to generate outputs: {e}")
        return False

    # Cleanup
    try:
        Path(tmp_path).unlink(missing_ok=True)
        logger.info(f"\n🧹 Cleaned up temp file")
    except:
        pass

    logger.info(f"\n" + "=" * 60)
    logger.info(f"✅ PIPELINE TEST SUCCESSFUL!")
    logger.info(f"=" * 60)

    return True


if __name__ == "__main__":
    # Use default audio file or from command line
    audio_file = sys.argv[1] if len(sys.argv) > 1 else "Eingang/Patient/KAH EGOSTATE (2).m4a"
    duration = int(sys.argv[2]) if len(sys.argv) > 2 else 30

    success = test_complete_pipeline(audio_file, duration)

    sys.exit(0 if success else 1)
