# Intelligent Pipeline

## Overview

The Intelligent Pipeline automatically analyzes audio quality and adapts transcription settings for optimal accuracy. No manual tuning required.

## Features

### 1. Audio Quality Analysis
- **SNR (Signal-to-Noise Ratio)**: Measures clarity vs. background noise
- **Clipping Detection**: Identifies distorted/overloaded audio
- **Silence Detection**: Analyzes speech density
- **Quality Score**: Combined metric (0.0 - 1.0)

### 2. Adaptive Model Selection

Quality scores automatically select the optimal Whisper model:

| Quality Score | Model | Preprocessing | Use Case |
|--------------|-------|---------------|----------|
| 0.0 - 0.4 | large | Aggressive | Noisy recordings, poor equipment |
| 0.4 - 0.6 | medium | Moderate | Typical phone recordings |
| 0.6 - 0.8 | medium | Light | Good quality recordings |
| 0.8 - 1.0 | small | None | Studio quality (faster) |

### 3. Adaptive Preprocessing

**Aggressive (Quality < 0.4)**:
- High-pass filter (removes rumble/hum)
- Noise reduction
- Volume normalization

**Moderate (Quality 0.4-0.6)**:
- Noise reduction
- Volume normalization

**Light (Quality 0.6-0.8)**:
- Volume normalization only

**Minimal (Quality > 0.8)**:
- No preprocessing (already excellent)

## Usage

### In SVT GUI

1. Open SVT: `python3 svt.py` or double-click `start_svt.sh`
2. Check "Intelligente Pipeline" in quality settings (enabled by default)
3. Process audio files normally

The pipeline automatically:
- Analyzes each audio file
- Displays quality metrics in progress log
- Selects optimal model
- Applies appropriate preprocessing
- Transcribes with best settings

### Programmatic Usage

```python
from audio_quality_analyzer import AudioQualityAnalyzer
from audio_preprocessor import AudioPreprocessor
import auto_transcriber_v4_emotion as v4

# Initialize components
analyzer = AudioQualityAnalyzer()
preprocessor = AudioPreprocessor()

# Analyze audio
metrics = analyzer.analyze_audio_file("recording.wav")
print(f"Quality: {metrics['quality_score']:.2f}")
print(f"SNR: {metrics['snr_db']:.1f} dB")

# Transcribe with intelligent pipeline
result = v4.transcribe_with_whisper(
    "recording.wav",
    model_size="medium",  # Will be overridden by quality analysis in GUI
    language="de",
    use_intelligent_pipeline=True,
    quality_score=metrics["quality_score"],
    quality_analyzer=analyzer,
    audio_preprocessor=preprocessor
)
```

## Technical Details

### Quality Scoring Algorithm

```python
quality_score = (
    0.5 * snr_score +        # 50% weight - signal clarity
    0.3 * clipping_score +   # 30% weight - distortion
    0.2 * silence_score      # 20% weight - speech density
)
```

**SNR Normalization**: 0-60 dB range mapped to 0-1
**Clipping Score**: `1.0 - (clipping_ratio * 10)`
**Silence Score**: Penalizes >50% silence

### Preprocessing Details

**Noise Reduction**: Spectral gating (noisereduce library)
- Stationary noise estimation
- Full reduction for low-quality audio

**Normalization**: RMS-based to -20 dBFS target
- Prevents clipping (0.95 safety margin)
- Maintains dynamic range

**High-Pass Filter**: 4th-order Butterworth at 80 Hz
- Removes rumble, AC hum, handling noise
- Preserves speech frequencies (>100 Hz)

## Testing

Run tests:

```bash
# Unit tests
python3 -m pytest test_audio_quality_analyzer.py -v
python3 -m pytest test_audio_preprocessor.py -v

# Integration tests
python3 -m pytest test_intelligent_pipeline_integration.py -v

# All tests
python3 -m pytest test_audio_quality_analyzer.py test_audio_preprocessor.py test_intelligent_pipeline_integration.py -v
```

## Performance

**Analysis overhead**: ~0.5-1 second per audio file
**Preprocessing time**:
- None (high quality): 0s
- Light: ~0.3s per minute of audio
- Aggressive: ~1-2s per minute of audio

**Accuracy improvement**: 10-30% WER reduction on low-quality audio (estimated based on preprocessing benefits)

## Troubleshooting

**"Module not found" errors**: Install dependencies
```bash
pip install --break-system-packages noisereduce librosa scipy soundfile
```

**Poor results despite high quality score**:
- Check if language setting is correct
- Verify audio actually contains speech
- Try manual model selection by disabling intelligent pipeline

**Processing too slow**:
- Disable intelligent pipeline for high-quality studio recordings
- Use smaller Whisper model manually
- Pre-process audio files offline in batch

**GUI not showing intelligent pipeline option**:
- Update to latest version of svt.py
- Check that imports are correct (AudioQualityAnalyzer, AudioPreprocessor)

## Architecture

```
┌─────────────────┐
│  Audio File     │
└────────┬────────┘
         │
         ▼
┌─────────────────────────┐
│ AudioQualityAnalyzer    │
│ - Calculate SNR         │
│ - Detect clipping       │
│ - Detect silence        │
│ - Compute quality score │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│ Model Selection Logic   │
│ Quality < 0.4 → large   │
│ Quality 0.4-0.6 → medium│
│ Quality 0.6-0.8 → medium│
│ Quality > 0.8 → small   │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│ AudioPreprocessor       │
│ - High-pass filter      │
│ - Noise reduction       │
│ - Volume normalization  │
│ (adaptive based on      │
│  quality score)         │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│ Whisper Transcription   │
│ - Selected model        │
│ - Preprocessed audio    │
│ - Word timestamps       │
│ - Confidence scores     │
└─────────────────────────┘
```

## Implementation Files

- `audio_quality_analyzer.py` - Quality analysis module
- `audio_preprocessor.py` - Preprocessing module
- `svt.py` - GUI integration (lines 43-45, 125-139, 311, 357-398)
- `auto_transcriber_v4_emotion.py` - Whisper integration (lines 791-858)
- `test_audio_quality_analyzer.py` - Quality analyzer tests (9 tests)
- `test_audio_preprocessor.py` - Preprocessor tests (6 tests)
- `test_intelligent_pipeline_integration.py` - Integration tests (5 tests)

## Future Enhancements

- [ ] Adaptive beam size selection based on quality
- [ ] Dynamic temperature adjustment for low-confidence segments
- [ ] Multi-speaker quality analysis (per-speaker optimization)
- [ ] Real-time quality monitoring during recording
- [ ] Custom quality thresholds in GUI
- [ ] Batch preprocessing mode for offline processing
- [ ] Quality report export (PDF/CSV)
- [ ] A/B testing framework for preprocessing strategies

## References

- **Whisper**: OpenAI's automatic speech recognition system
- **noisereduce**: Noise reduction using spectral gating
- **librosa**: Audio analysis library
- **SciPy**: Signal processing (filters)
