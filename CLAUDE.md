# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Super Semantic Whisper** is a multi-component system that combines WhatsApp audio transcription with deep semantic analysis. It consists of three major subsystems:

1. **WhisperSprecherMatcher**: Audio transcription with speaker recognition and memory-based learning
2. **Super Semantic Processor**: Semantic analysis engine that transforms chat histories into structured semantic representations
3. **WhatsApp Auto Transcriber**: Next-generation modular file watcher system for automatic transcription

## Core Commands

### Running the System

```bash
# Main entry point - interactive launcher
python3 start_super_semantic.py

# GUI mode (recommended for most users)
python3 super_semantic_gui.py

# Direct transcription (V3 - recommended with date/time extraction)
python3 auto_transcriber_v3.py --local

# Emotion-aware transcription (V4)
python3 auto_transcriber_v4_emotion.py

# Build speaker memory profiles from existing transcripts
python3 build_memory_from_transcripts.py

# Run semantic integration demo
python3 demo_semantic_integration.py
```

### Therapeutic Transcription System (NEW)

```bash
# Launch professional GUI (recommended)
python3 therapeutic_transcriber_gui.py

# Run tests
python3 -m pytest test_prosody_analyzer.py test_transcriber_v4_prosody.py test_memory_prosody.py -v

# Integration tests
python3 -m pytest test_integration_therapeutic.py -v

# Direct usage (programmatic)
python3 -c "
from prosody_analyzer import ProsodyAnalyzer
analyzer = ProsodyAnalyzer()
prosody = analyzer.extract_from_file('audio.wav')
print(prosody)
"
```

### Testing

```bash
# Test person initialization
python3 test_initialize_person.py

# Note: pytest is not currently configured in this project
```

### Dependencies

```bash
# Install all dependencies
pip3 install -r requirements.txt

# For emotion analysis features (V4):
pip3 install librosa textblob scikit-learn

# GUI dependencies (manual installation required):
# macOS: brew install python-tk
# Ubuntu: sudo apt-get install python3-tk
```

## Architecture

### Directory Structure & Data Flow

```
Super_semantic_whisper/
├── Eingang/                        # INPUT: Raw audio files organized by speaker
│   ├── ben/                        # Speaker-specific folders
│   ├── zoe/                        # Priority processing for this folder
│   └── schroeti/
├── Transkripte_LLM/                # OUTPUT: LLM-optimized transcripts (.md)
├── Memory/                         # Speaker profiles (YAML) - learning system
│   ├── ben.yaml                    # Language patterns, sentiment, topics
│   ├── zoe.yaml
│   └── schroeti.yaml
├── whisper_speaker_matcher/        # Legacy organization (fallback)
│   ├── Eingang/
│   └── Memory/
└── whatsapp_auto_transcriber/      # Next-gen modular system (Phase 1)
    ├── src/                        # Modular components
    │   ├── file_watcher.py
    │   ├── audio_processor.py
    │   ├── speaker_detector.py
    │   └── monitoring.py
    └── config/config.yaml
```

### Key Processing Flow

1. **Audio Ingestion**: Audio files (.opus, .wav, .mp3, .m4a, .ogg) placed in `Eingang/{speaker}/`
2. **Transcription**: Whisper processes audio with date/time extraction from filenames
3. **Emotion Analysis** (V4): Librosa + TextBlob analyze audio features and text sentiment
4. **Speaker Recognition**: Multi-method approach (filename, keywords, context, memory-based)
5. **Memory Building**: YAML profiles updated with speech patterns, topics, sentiment ratios
6. **Semantic Processing**: Super Semantic Processor analyzes transcripts for markers, threads, relationships
7. **Output**: Structured JSON + human-readable Markdown summaries

### Component Integration

The system integrates multiple external marker systems located in parent directories:

- `../ALL_SEMANTIC_MARKER_TXT/` - Semantic marker repository (63+ markers)
- `../Marker_assist_bot/` - FRAUSAR marker management system
- `../Marker_assist_bot/semantic_grabber_library.yaml` - Pattern matching definitions
- `../MARSAP/` and `../MARSAPv2/` - CoSD drift analysis

These are dynamically loaded by `super_semantic_processor.py` through sys.path manipulation.

### Processing Priority

The transcription system prioritizes the `Zoe/` folder first, then processes other folders alphabetically. Within each folder, newest recordings are processed first.

### Therapeutic Transcription Pipeline (NEW)

```
Audio Input
    ↓
[Whisper Transcription]
    ├─> Text
    ├─> Segments with timestamps
    └─> Confidence scores (avg_logprob, no_speech_prob)
    ↓
[Emotion Analysis]
    ├─> Text sentiment (TextBlob)
    ├─> Audio emotion (Whisper audio features)
    └─> Combined emotional assessment
    ↓
[Prosody Extraction]
    ├─> Pitch (F0 mean, std, contour)
    ├─> Tempo (BPM, speech rate)
    └─> Energy (RMS, dynamic range)
    ↓
[Confidence Marking]
    └─> Mark segments with confidence < threshold as [UNSICHER:score]
    ↓
[Memory Update]
    ├─> Update speaker prosody_patterns (running averages)
    ├─> Update statistics, topics, characteristics
    └─> Save to Memory/{speaker}.yaml
    ↓
[Output: Therapeutic Transcript]
    ├─> Markdown with all metadata
    ├─> Prosody features summary
    ├─> Quality warnings
    └─> Marked low-confidence segments
```

**Key Architectural Changes:**
- **Prosody integration**: New `prosody_analyzer.py` module extracts pitch/tempo/energy
- **Enhanced V4**: `auto_transcriber_v4_emotion.py` now includes prosody in emotion analysis
- **Memory enhancement**: Speaker YAML profiles now include `prosody_patterns` section
- **Confidence scoring**: Whisper output converted to 0-1 confidence scores
- **Quality marking**: Low-confidence segments marked inline with [UNSICHER:score]
- **GUI**: New `therapeutic_transcriber_gui.py` provides professional one-click workflow

## Important Technical Details

### Audio File Naming Convention

WhatsApp audio files follow the pattern: `WhatsApp Audio YYYY-MM-DD at HH.MM.SS.opus`

The V3 and V4 transcribers extract this timestamp and use it for:
- Output filename: `YYYY-MM-DD_HH-MM-SS_speaker_originalname_transkript.md`
- Metadata in transcript header
- Temporal analysis in semantic processing

### Memory System Structure

Speaker profiles (`Memory/*.yaml`) contain:
- **statistics**: avg_sentence_length, most_common_words, sentiment (positive/negative/ratio)
- **topics**: Counters for technology, business, personal, etc.
- **characteristics**: Auto-generated descriptors (technisch_orientiert, bedächtig, präzise)
- **interactions**: Last 50 transcriptions with timestamps
- **metadata**: name, last_updated, total_interactions

### Semantic Message Structure

The `super_semantic_processor.py` creates `SemanticMessage` dataclasses with:
- id, timestamp, sender, content, type (text/audio/image/document)
- emotion: Dict of emotional valence scores
- markers: List of detected semantic markers
- semantic_scores: Numerical scores for various dimensions
- metadata: Additional context

### Emotion Detection (V4)

The emotional analyzer uses a multi-source approach:
1. Load emotional markers from existing marker system (ALL_SEMANTIC_MARKER_TXT)
2. Extract audio features using librosa (if available): pitch, energy, tempo, spectral features
3. Perform text sentiment analysis using TextBlob (if available)
4. Combine audio + text features for overall emotional classification
5. Output dominant emotion with confidence and valence score in transcript

### Prosody Data Structure

In Memory YAML profiles:

```yaml
prosody_patterns:
  pitch_profile:
    mean_pitch: 147.8          # Hz, running average
    pitch_variability: 19.4    # Standard deviation
    sample_count: 15           # Number of samples
  tempo_profile:
    mean_bpm: 118.5           # Beats per minute
    mean_speech_rate: 4.3     # Syllables per second
    sample_count: 15
  energy_profile:
    mean_energy: 0.045        # RMS energy
    energy_variability: 0.012 # Standard deviation
    mean_dynamic_range: 0.28  # Max - min
    sample_count: 15
```

### Confidence Score Calculation

Whisper provides:
- `avg_logprob`: Average log probability (negative)
- `no_speech_prob`: Probability of silence

Conversion to confidence:
```python
confidence = exp(avg_logprob) * (1 - no_speech_prob)
```

Range: 0.0 (unreliable) to 1.0 (very confident)

Therapeutic threshold: 0.5 (configurable)

### Transcription Output Format

All transcripts are formatted as Markdown with:
```markdown
# WhatsApp Audio Transkription / # Transkript: {filename}

**Chat mit:** {speaker}
**Aufnahme am:** DD.MM.YYYY um HH:MM:SS
**Verarbeitet am:** DD.MM.YYYY um HH:MM:SS
**Original-Datei:** {original_filename}

[V4 only]
**Dominante Emotion:** {emotion} {emoji}
**Emotionale Valenz:** {score}

## Zeitstempel:
- **Aufnahme-Datum:** YYYY-MM-DD
- **Aufnahme-Uhrzeit:** HH:MM:SS

## Transkription:
{transcribed_text}

## Kontext für LLM:
Diese Nachricht wurde am ... aufgenommen
```

This format is optimized for LLM consumption and semantic processing.

## Development Notes

### FFmpeg Dependency

FFmpeg is required for audio conversion. Installation:
- macOS: `brew install ffmpeg`
- Ubuntu: `sudo apt install ffmpeg`

Verify with: `ffmpeg -version`

### Python Version

Requires Python 3.8+. Tested with Python 3.12.3.

### Logging

Most scripts create detailed logs:
- `transcription.log` - V3 transcriber output
- `transcription_v4_emotion.log` - V4 with emotion analysis
- Console output with timestamps

### Local vs Google Drive Mode

The system supports both local operation and Google Drive sync:
- Local: Uses `./Eingang/` and `./Memory/`
- Google Drive: Syncs with remote directories (see `google_drive_sync.py`)
- Automatic fallback to local if Drive unavailable

Run with `--local` flag to force local mode: `python3 auto_transcriber_v3.py --local`

### GUI vs CLI

The `start_super_semantic.py` launcher provides:
1. GUI mode - User-friendly interface for configuration
2. CLI mode - Command-line prompts for paths
3. Demo mode - Creates sample data and runs full pipeline
4. Help mode - Displays usage information

Use GUI for initial setup and configuration, CLI for automation/scripting.

### Marker Set Selection

The Super Semantic Processor accepts a `marker_set` parameter to choose different marker collections:
- `All_Markers` - Complete marker set
- `Trauma` - Trauma-specific markers
- Custom YAML files can be provided

This is configured in the GUI or passed to `process_everything()`.

### Next-Gen Modular System

The `whatsapp_auto_transcriber/` directory contains a modular refactoring (Phase 1):
- Separation of concerns: file watching, audio processing, speaker detection
- Configuration via YAML
- Designed for easier testing and maintenance
- Gradually integrating V4 emotion logic

This is a work in progress and not yet the primary entry point.

## Common Workflows

### Adding a New Speaker

1. Create a folder in `Eingang/{new_speaker_name}/`
2. Place audio files there
3. Run `python3 auto_transcriber_v3.py --local`
4. Memory profile automatically created in `Memory/{new_speaker_name}.yaml`

### Custom Semantic Analysis

1. Prepare WhatsApp export (.txt) and/or transcripts directory
2. Optionally create custom marker YAML
3. Run GUI: `python3 super_semantic_gui.py`
4. Select marker set and input/output paths
5. Results: JSON + Markdown summary

### Extending Emotional Markers

1. Add marker files to `../ALL_SEMANTIC_MARKER_TXT/Former_NEW_MARKER_FOLDERS/emotions/`
2. V4 automatically loads on next run
3. Or provide custom markers in `EmotionalAnalyzer._create_default_emotional_markers()`

## Important Constraints

- The system expects parent directories for marker systems (`../ALL_SEMANTIC_MARKER_TXT/`, etc.)
- Transcription quality depends on audio quality and FFmpeg installation
- Speaker recognition improves over time as Memory profiles build
- Large chat histories may take significant time to process
- GUI requires tkinter (not always available via pip)
