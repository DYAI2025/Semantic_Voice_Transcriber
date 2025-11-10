# Therapeutic Transcription System - User Guide

## Overview

This system provides professional-grade audio transcription optimized for therapeutic use cases. It combines OpenAI Whisper transcription with emotion analysis, prosody extraction, and comprehensive quality assurance.

## Key Features for Therapeutic Use

### 1. High-Quality Transcription
- **Multiple model sizes**: Choose based on accuracy needs (medium recommended)
- **Confidence scoring**: Every segment rated for reliability
- **Quality warnings**: Low-confidence segments clearly marked

### 2. Emotional Analysis
- **Text sentiment**: Analyze emotional content of words
- **Audio emotion**: Detect emotional coloring in voice
- **Combined assessment**: Holistic emotion detection

### 3. Prosody Extraction (Voice-Marker 2.0 Ready)
- **Pitch analysis**: F0 contour, mean, variability
- **Tempo/rhythm**: Speaking rate, pauses
- **Energy**: Loudness, dynamic range

### 4. Speaker Memory System
- **Learning profiles**: System improves over time
- **Prosody patterns**: Voice characteristics stored
- **Interaction history**: Track changes over sessions

## Quick Start

### Installation

```bash
cd /path/to/Super_semantic_whisper
pip3 install -r requirements.txt

# Install additional dependencies for emotion/prosody
pip3 install librosa textblob scikit-learn
```

### Basic Usage

1. **Launch GUI**:
   ```bash
   python3 therapeutic_transcriber_gui.py
   ```

2. **Configure**:
   - Set input directory (where audio files are)
   - Set output directory (where transcripts go)
   - Choose Whisper model (medium recommended)
   - Set confidence threshold (0.5 recommended)

3. **Select Speakers**:
   - Click "Sprecher aktualisieren"
   - Select one or more speakers to process

4. **Start**:
   - Click "🚀 Transkription starten"
   - Monitor progress in real-time
   - View log for details

## Understanding Output Files

### Transcript Format

Each transcript includes:

```markdown
# Therapeutisches Transkript

**Sprecher:** john_doe
**Original-Datei:** WhatsApp Audio 2025-11-10 at 14.30.45.opus
**Verarbeitet am:** 2025-11-10 15:22:10
**Confidence:** 0.87

**Dominante Emotion:** neutral
**Emotionale Valenz:** 0.12

## Prosody-Merkmale
- **Pitch:** 145.3 Hz (±18.2)
- **Tempo:** 115 BPM
- **Sprechrate:** 4.2 Silben/Sek
- **Energie:** 0.042

## ⚠️ Qualitäts-Hinweise
2 Segment(e) mit niedriger Confidence erkannt.
Diese sind im Text mit [UNSICHER:score] markiert.

## Transkription

Hello, this is a test. [UNSICHER:0.42] The unclear part is marked.
The rest of the transcription continues normally.
```

### Memory Profiles

Located in `Memory/{speaker}.yaml`:

```yaml
name: john_doe
last_updated: '2025-11-10T15:22:10'
total_interactions: 15
prosody_patterns:
  pitch_profile:
    mean_pitch: 147.8
    pitch_variability: 19.4
    sample_count: 15
  tempo_profile:
    mean_bpm: 118.5
    mean_speech_rate: 4.3
    sample_count: 15
  energy_profile:
    mean_energy: 0.045
    energy_variability: 0.012
    mean_dynamic_range: 0.28
    sample_count: 15
```

## Quality Assurance

### Confidence Scores

- **≥ 0.7**: High confidence - reliable transcription
- **0.5 - 0.7**: Medium confidence - generally good
- **< 0.5**: Low confidence - marked with [UNSICHER:score]

### When to Review Manually

Review transcripts if:
- Overall confidence < 0.6
- Multiple [UNSICHER] markers
- Critical therapeutic content
- Speaker is new (first few sessions)

### Improving Quality

1. **Audio quality**:
   - Use good recording environment
   - Minimize background noise
   - Ensure clear speech

2. **Model selection**:
   - `medium`: Best balance for German therapeutic use
   - `large`: Maximum accuracy (slower, more memory)
   - `small`: Faster but less accurate

3. **Language setting**:
   - `de`: German (recommended)
   - `auto`: Auto-detect (use if mixed languages)

## Advanced Features

### Prosody for Voice-Marker 2.0

The system extracts prosodic features that will power Voice-Marker 2.0:

- **Pitch patterns**: Detect stress, emphasis, emotional states
- **Rhythm**: Speaking style, hesitations, confidence
- **Energy**: Engagement level, emotional intensity

These features are stored in memory profiles and available for future analysis.

### Batch Processing

Process multiple speakers efficiently:

1. Organize files: `Eingang/{speaker}/audio_files.opus`
2. Select all speakers in GUI
3. System processes sequentially
4. All results in `Transkripte_LLM/`

## Troubleshooting

### "Whisper model download failed"
- Ensure internet connection
- First run downloads model (large file)
- Subsequent runs use cached model

### "librosa not available"
- Install: `pip3 install librosa soundfile`
- Prosody features require librosa

### "Low confidence on good audio"
- Try larger model (medium -> large)
- Check if audio is actually clear
- Some speakers need multiple sessions to build profile

### "GUI doesn't start"
- Install tkinter: `brew install python-tk` (macOS)
- Or: `sudo apt-get install python3-tk` (Ubuntu)

## Best Practices for Therapeutic Use

1. **Consistent environment**: Record in same setting
2. **Regular processing**: Process sessions shortly after recording
3. **Review low-confidence**: Always check [UNSICHER] segments
4. **Build profiles**: Multiple sessions improve accuracy
5. **Backup memory**: Keep Memory/ directory backed up
6. **Document sessions**: Use consistent naming for audio files

## Technical Details

### Architecture

```
Audio File
    ↓
Whisper Transcription (with confidence)
    ↓
Emotion Analysis (text + audio)
    ↓
Prosody Extraction (pitch, tempo, energy)
    ↓
Memory Update (speaker profiles)
    ↓
Therapeutic Transcript (markdown)
```

### File Organization

```
Eingang/                    # Input
  speaker1/
    audio1.opus
    audio2.opus
  speaker2/
    audio3.opus

Transkripte_LLM/            # Output
  audio1_transkript.md
  audio2_transkript.md
  audio3_transkript.md

Memory/                     # Profiles
  speaker1.yaml
  speaker2.yaml
```

## Support

For issues or questions:
- Check logs in GUI
- Review CLAUDE.md for technical details
- Test with small audio file first
