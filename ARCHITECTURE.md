# SVT Architecture - Production-Ready Design

**Version:** 2.0
**Date:** 2025-11-17
**Status:** Production Architecture

---

## Design Principles

### 1. Portability
- **Cross-platform:** Linux, Windows, macOS
- **Dependencies:** Clearly documented in requirements.txt
- **Configuration:** YAML-based, environment-agnostic

### 2. Reliability
- **Error Handling:** Every layer has fallback mechanisms
- **Validation:** Input/output validation at all boundaries
- **Logging:** Comprehensive logging for debugging

### 3. Maintainability
- **Clean Architecture:** Separation of concerns
- **Modularity:** Each component independently testable
- **Documentation:** Code + architecture docs

### 4. Scalability
- **Chunking:** Handles audio files of any length
- **Caching:** Avoids redundant processing
- **Resource Management:** Memory-efficient processing

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         SVT GUI                              │
│                    (User Interface)                          │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                 Transcription Orchestrator                   │
│           (auto_transcriber_v4_emotion.py)                   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         Quality Monitoring & Validation              │  │
│  │  - Input validation                                  │  │
│  │  - Output quality checks                             │  │
│  │  - Error detection & recovery                        │  │
│  └──────────────────────────────────────────────────────┘  │
└──────────────┬───────────────────────────────────────────────┘
               │
               ├──────────────────────┬─────────────────────────┐
               ▼                      ▼                         ▼
┌────────────────────┐  ┌────────────────────┐  ┌────────────────────┐
│  Audio Processing  │  │ Prosody Analysis   │  │ Speaker Diarization│
│                    │  │                    │  │                    │
│ - Quality Check    │  │ - Tempo Extract    │  │ - pyannote.audio   │
│ - Preprocessing    │  │ - Pitch Extract    │  │ - Overlap Detect   │
│ - Chunking         │  │ - Energy Extract   │  │ - Speaker Mapping  │
│ - Format Convert   │  │ - Pause Detect     │  │ - Error Recovery   │
└────────────────────┘  └────────────────────┘  └────────────────────┘
               │                      │                         │
               └──────────────┬───────┴─────────────────────────┘
                              ▼
               ┌────────────────────────────────────┐
               │    Whisper Transcription Engine    │
               │                                    │
               │  - Model Selection (Quality-based) │
               │  - Confidence Scoring              │
               │  - Language Detection              │
               │  - Segment Extraction              │
               └──────────────┬─────────────────────┘
                              │
                              ▼
               ┌────────────────────────────────────┐
               │   Semantic Analysis Pipeline       │
               │                                    │
               │  ┌──────────────────────────────┐ │
               │  │  ATO Marker Detection        │ │
               │  │  - Curated 40 markers        │ │
               │  │  - Confidence filtering      │ │
               │  │  - Context-aware matching    │ │
               │  └──────────────────────────────┘ │
               │                                    │
               │  ┌──────────────────────────────┐ │
               │  │  Emotion Analysis            │ │
               │  │  - TextBlob sentiment        │ │
               │  │  - Audio-based features      │ │
               │  └──────────────────────────────┘ │
               └──────────────┬─────────────────────┘
                              │
                              ▼
               ┌────────────────────────────────────┐
               │    Interpretation Layer (NEW)      │
               │                                    │
               │  - Multi-modal fusion              │
               │  - Prosody + Markers + Context     │
               │  - Plausibility scoring            │
               │  - Clinical insights               │
               └──────────────┬─────────────────────┘
                              │
                              ▼
               ┌────────────────────────────────────┐
               │      Output Formatter              │
               │                                    │
               │  - Speaker Configuration           │
               │  - Therapeutic Markdown            │
               │  - Enhanced HTML                   │
               │  - JSON sidecar                    │
               │  - PDF export                      │
               └──────────────┬─────────────────────┘
                              │
                              ▼
               ┌────────────────────────────────────┐
               │    Quality Validation (POST)       │
               │                                    │
               │  ✓ Speaker labels present?         │
               │  ✓ ATO markers diverse?            │
               │  ✓ Confidence acceptable?          │
               │  ✓ Prosody features complete?      │
               │  ✓ Format valid?                   │
               └──────────────┬─────────────────────┘
                              │
                              ▼
               ┌────────────────────────────────────┐
               │     Output Files + Report          │
               │                                    │
               │  - Transcripts (MD, HTML, PDF)     │
               │  - Data (JSON)                     │
               │  - Quality Report (JSON)           │
               │  - Warnings & Recommendations      │
               └────────────────────────────────────┘
```

---

## Layer Descriptions

### Layer 1: User Interface (SVT GUI)
**Responsibility:** User interaction, file selection, settings

**Key Files:**
- `svt.py` - Main GUI application
- `svt_gui_helpers.py` - Helper functions

**Error Handling:**
- File not found → User-friendly error message
- Invalid settings → Validation before processing
- Process crashes → Automatic log capture

---

### Layer 2: Transcription Orchestrator
**Responsibility:** Coordinate all processing steps

**Key Files:**
- `auto_transcriber_v4_emotion.py`

**Quality Gates:**
1. **Pre-validation:** Audio file exists, format supported, not corrupted
2. **Mid-processing:** Whisper confidence > threshold, prosody extraction success
3. **Post-validation:** All expected outputs generated, quality metrics met

**Error Recovery:**
- Speaker diarization fails → Continue without speaker labels (warn user)
- Prosody extraction fails → Continue without prosody (warn user)
- ATO detection fails → Continue without markers (warn user)
- **NEVER** fail completely unless audio cannot be transcribed

---

### Layer 3: Audio Processing
**Responsibility:** Prepare audio for transcription

**Key Files:**
- `audio_quality_analyzer.py` - SNR, clipping, silence detection
- `audio_preprocessor.py` - Noise reduction, normalization
- `audio_chunker.py` - Split long audio into manageable chunks

**Validation:**
- ✓ Sample rate valid (8000-48000 Hz)
- ✓ Duration > 0
- ✓ Channels = 1 or 2
- ✓ File readable

**Fallbacks:**
- Bad quality → Suggest preprocessing
- Very long → Automatic chunking
- Multi-channel → Convert to mono

---

### Layer 4: Prosody Analysis
**Responsibility:** Extract acoustic features

**Key Files:**
- `prosody_extractor.py`

**Features Extracted:**
- **Tempo:** Words per minute (WPM)
- **Pitch:** F0 using Parselmouth
- **Energy:** RMS and dB levels
- **Pauses:** Silence > 1000ms

**Baseline Calculation:**
- Global means across all segments
- Used for deviation detection
- Stored in Memory/ profiles

**Validation:**
- ✓ At least 5 segments for baseline
- ✓ Pitch within human range (50-500 Hz)
- ✓ Energy > 0
- ✓ Tempo reasonable (30-300 WPM)

---

### Layer 5: Speaker Diarization
**Responsibility:** Identify who speaks when

**Key Files:**
- `speaker_diarizer.py`

**Models:**
- pyannote.audio 3.1
- Requires Hugging Face token

**Error Handling:**
```python
try:
    speakers = diarize_audio(audio_path)
except HFTokenError:
    log.warning("HF token missing - continuing without speaker labels")
    speakers = None  # Graceful degradation
except DiarizationError as e:
    log.error(f"Diarization failed: {e}")
    speakers = None  # Continue processing
```

**Fallback Strategy:**
- No token → Skip diarization, label all as "Unknown"
- Diarization crashes → Skip, label all as "Unknown"
- **Always warn user in output report**

---

### Layer 6: Whisper Transcription
**Responsibility:** Speech-to-text

**Models:** tiny, base, small, medium, large

**Selection Strategy:**
```python
if audio_quality > 0.8:
    model = "small"  # Fast, good enough
elif audio_quality > 0.6:
    model = "medium"  # Better accuracy
else:
    model = "large"  # Maximum accuracy for poor audio
```

**Confidence Scoring:**
```python
confidence = exp(avg_logprob) * (1 - no_speech_prob)
```

**Validation:**
- ✓ Segments returned
- ✓ Text not empty
- ✓ Timestamps sequential

---

### Layer 7: Semantic Analysis
**Responsibility:** Detect markers and emotions

**Key Files:**
- `ato_marker_integration.py` - ATO marker wrapper
- `ato_marker_detector.py` - Core detection engine

**Curated Markers:**
- 40 high-quality markers
- Confidence threshold: 0.6
- Max per segment: 5

**Validation:**
- ✓ Markers are from curated set
- ✓ Confidence values 0.0-1.0
- ✓ No more than max_markers per segment

**Error Handling:**
- Detector unavailable → Empty marker arrays (warn user)
- Detection crashes → Empty arrays for affected segments
- Invalid marker IDs → Filter out, log warning

---

### Layer 8: Interpretation Layer (NEW)
**Responsibility:** Multi-modal analysis and clinical insights

**Input:**
- Prosody features (tempo, pitch, energy, pauses)
- ATO markers (semantic patterns)
- Speaker information
- Context (previous/next utterances)

**Output:**
- **Clinical interpretation** - Plausible therapeutic insights
- **Confidence score** - How certain is the interpretation
- **Supporting evidence** - Which features support this

**Example:**
```json
{
  "segment_id": 42,
  "interpretation": {
    "primary": "Emotional breakthrough moment",
    "confidence": 0.82,
    "evidence": {
      "prosody": "Energy ↑ (+48%), Pitch ↑ (+22%), Long pause before",
      "markers": ["ATO_BREAKTHROUGH", "ATO_INSIGHT"],
      "context": "Following 3 segments of ATO_RESISTANCE"
    },
    "clinical_note": "Patient overcomes resistance, shows authentic emotion"
  }
}
```

**Validation:**
- ✓ Interpretation is plausible given evidence
- ✓ Confidence matches evidence strength
- ✓ No contradictory signals

---

### Layer 9: Output Formatter
**Responsibility:** Generate human-readable outputs

**Key Files:**
- `output_formatter.py`

**Speaker Configuration:**
- MODE_ANONYMOUS: "Therapeut", "Patient"
- MODE_LETTERS: "Speaker A", "B"
- MODE_NAMES: Actual names
- MODE_CUSTOM: User-defined mapping

**Formats:**
- **Markdown:** Therapeutic format with metadata sidebar
- **JSON:** Structured data with all features
- **HTML:** Color-coded, interactive
- **PDF:** Professional, printable

**Validation:**
- ✓ All segments formatted
- ✓ Speaker labels not "Unknown" (if diarization ran)
- ✓ Markers present (if detection ran)
- ✓ Files created successfully

---

### Layer 10: Quality Validation (POST)
**Responsibility:** Verify output quality

**Checks:**
```python
def validate_transcript_quality(transcript_json):
    issues = []

    # 1. Speaker labels
    if all(s['speaker'] is None for s in transcript_json['segments']):
        issues.append({
            "severity": "WARNING",
            "component": "Speaker Diarization",
            "message": "No speaker labels detected",
            "recommendation": "Enable diarization or check HF token"
        })

    # 2. ATO markers
    marker_count = sum(len(s.get('ato_markers', [])) for s in transcript_json['segments'])
    if marker_count == 0:
        issues.append({
            "severity": "WARNING",
            "component": "ATO Detection",
            "message": "No ATO markers detected",
            "recommendation": "Check marker detector availability"
        })
    elif marker_count < len(transcript_json['segments']) * 0.1:
        issues.append({
            "severity": "INFO",
            "component": "ATO Detection",
            "message": "Very few markers detected",
            "recommendation": "Lower confidence threshold or check text content"
        })

    # 3. Confidence
    avg_conf = sum(s['confidence'] for s in transcript_json['segments']) / len(transcript_json['segments'])
    if avg_conf < 0.5:
        issues.append({
            "severity": "ERROR",
            "component": "Transcription Quality",
            "message": f"Very low confidence: {avg_conf:.1%}",
            "recommendation": "Check audio quality, try larger Whisper model"
        })
    elif avg_conf < 0.7:
        issues.append({
            "severity": "WARNING",
            "component": "Transcription Quality",
            "message": f"Low confidence: {avg_conf:.1%}",
            "recommendation": "Review transcript carefully, consider re-recording"
        })

    # 4. Prosody features
    missing_prosody = sum(1 for s in transcript_json['segments'] if not s.get('prosody'))
    if missing_prosody > 0:
        issues.append({
            "severity": "WARNING",
            "component": "Prosody Analysis",
            "message": f"{missing_prosody} segments missing prosody",
            "recommendation": "Enable prosody analysis in settings"
        })

    return issues
```

**Output:** Quality report JSON saved alongside transcript

---

## Error Handling Strategy

### Principle: Graceful Degradation
**Never crash completely. Always produce SOMETHING useful.**

```python
# Example: Speaker Diarization
try:
    speakers = run_speaker_diarization(audio_path, hf_token)
    quality_report['speaker_diarization'] = "SUCCESS"
except HFTokenError:
    logger.warning("HF token missing - skipping diarization")
    speakers = None
    quality_report['speaker_diarization'] = "SKIPPED - No HF token"
    quality_report['warnings'].append("Speaker labels unavailable")
except Exception as e:
    logger.error(f"Diarization failed: {e}")
    speakers = None
    quality_report['speaker_diarization'] = f"FAILED - {str(e)}"
    quality_report['warnings'].append("Speaker diarization failed")

# Continue processing regardless
segments = merge_speakers_with_segments(transcription, speakers)  # Handles None gracefully
```

---

## Configuration Management

### Environment Variables (.env)
```bash
HF_TOKEN=hf_...  # For speaker diarization
OPENAI_API_KEY=sk-...  # Optional, for psychoanalysis dashboard
```

### Config Files (YAML)
```yaml
# config/svt_config.yaml
processing:
  default_model: "small"
  enable_preprocessing: true
  enable_chunking: true
  chunk_duration: 300  # 5 minutes

prosody:
  tempo_threshold: 20.0  # ±20%
  pitch_threshold: 15.0  # ±15%
  energy_threshold: 25.0  # ±25%
  pause_threshold: 1000  # ms

ato_markers:
  use_curated: true
  confidence_threshold: 0.6
  max_per_segment: 5

speaker_config:
  mode: "anonymous"  # or "letters", "names", "custom"
  custom_mapping: {}

output:
  generate_markdown: true
  generate_json: true
  generate_html: true
  generate_pdf: true
  generate_enhanced_html: true
```

---

## Testing Strategy

### Unit Tests
- Each component testable in isolation
- Mock external dependencies (Whisper, pyannote)

### Integration Tests
- Full pipeline with sample audio
- Verify all outputs generated

### Quality Tests
- Validation layer catches issues
- Known-good transcripts as benchmarks

---

## Deployment Checklist

### System Requirements
```
Python: >= 3.10
RAM: >= 8 GB (16 GB recommended)
Storage: >= 5 GB for models
GPU: Optional (10x faster with CUDA)
```

### Installation Script
```bash
#!/bin/bash
# install_svt.sh

# 1. Install system dependencies
sudo apt install python3 python3-pip ffmpeg portaudio19-dev

# 2. Create virtual environment
python3 -m venv svt_env
source svt_env/bin/activate

# 3. Install Python packages
pip install -r requirements.txt
pip install -r requirements_emotion.txt

# 4. Download Whisper models (optional, lazy loaded)
python3 -c "import whisper; whisper.load_model('small')"

# 5. Configure HF token
read -sp "Enter Hugging Face token (or press Enter to skip): " HF_TOKEN
if [ ! -z "$HF_TOKEN" ]; then
    echo "HF_TOKEN=$HF_TOKEN" >> .env
    echo "✅ HF token configured"
fi

# 6. Test installation
python3 -c "from output_formatter import SpeakerConfig; print('✅ SVT installed successfully')"

echo "✅ Installation complete!"
echo "   Start with: python3 svt.py"
```

---

## Monitoring & Logging

### Log Levels
```python
logging.DEBUG    # Detailed info for debugging
logging.INFO     # Progress updates
logging.WARNING  # Degraded functionality (e.g., missing speaker labels)
logging.ERROR    # Component failure (but processing continues)
logging.CRITICAL # Complete failure (cannot continue)
```

### Quality Metrics Tracked
- Transcription confidence (per segment, overall)
- Speaker diarization success rate
- ATO marker diversity (unique markers / total segments)
- Prosody coverage (segments with features / total segments)
- Processing time (per stage)

---

## Version Control & Updates

### Semantic Versioning
```
MAJOR.MINOR.PATCH
2.0.0 - Production architecture release
```

### Changelog
All changes documented in CHANGELOG.md

### Backward Compatibility
- Config files validated with schema
- Old transcripts still readable
- Migrations for breaking changes

---

## Future Architecture Goals

### Phase 3: Real-time Processing
- Streaming audio input
- Incremental transcription
- Live speaker diarization
- WebSocket API

### Phase 4: Multi-language Support
- Auto-detect language
- Per-language marker sets
- Multilingual dashboards

### Phase 5: Cloud Deployment
- Docker containers
- REST API
- Cloud storage integration
- Multi-tenant support

---

**Last Updated:** 2025-11-17
**Maintained By:** TransSemantic Development Team
