# QWEN.md - Project Context for TransSemantic

## Project Overview

The **TransSemantic** project is a comprehensive semantic voice analysis and transcription system designed primarily for therapeutic applications. It combines state-of-the-art speech-to-text technology with advanced prosody analysis, emotion detection, and semantic marker recognition to provide deep insights into spoken communication.

The project consists of multiple interconnected systems:
- **Semantic Voice Transcriber (SVT)**: Professional audio transcription with prosody analysis
- **Super Semantic Processor**: WhatsApp/Audio analysis with semantic pattern recognition
- **ATO Marker System**: Atomic linguistic markers for behavioral analysis
- **Emotion Detection Engine**: Multi-modal emotional analysis from text and audio

## Project Architecture

### Core Components

1. **SVT (Semantic Voice Transcriber)**
   - Advanced Whisper-based transcription
   - Prosody extraction (tempo, pitch, energy, pauses)
   - Speaker diarization
   - Overlapped speech detection
   - Confidence scoring
   - Intelligent pipeline with quality analysis

2. **Super Semantic Processor**
   - WhatsApp export analysis
   - Audio transcription processing
   - Semantic marker analysis
   - Emotional arc tracking
   - Relationship mapping between messages
   - Semantic thread identification

3. **ATO (Atomic) Markers System**
   - YAML-based marker definitions
   - 60+ atomic semantic markers
   - Correlation engine for audio-semantic analysis
   - Therapeutic and behavioral pattern detection

### Directory Structure

```
Super_semantic_whisper/
├── svt.py                    # Main SVT GUI application
├── auto_transcriber_v4_emotion.py  # Whisper transcription with emotion
├── super_semantic_processor.py     # Main semantic processor
├── prosody_extractor.py            # Prosody analysis engine
├── speaker_diarizer.py             # Speaker identification
├── output_formatter.py             # Output format management
├── ATO_*.yaml                      # Atomic semantic markers
├── ato_correlation_*.py            # Correlation engine
├── Eingang/                        # Input directory for audio files
├── Transkripte_LLM/                # Transcription output directory
├── Memory/                         # Speaker profile storage
├── VP_ATO/                         # Voice pattern atomic markers
├── LD3.4_*                        # various marker sets
└── requirements*.txt              # Project dependencies
```

## Key Functionalities

### 1. Audio Transcription with Prosody Analysis
- High-quality Whisper-based transcription
- Four core prosodic features:
  - **Tempo**: Words per minute with deviation detection
  - **Pitch**: F0 analysis in Hz using Parselmouth/Praat
  - **Energy**: RMS and dB values
  - **Pausen**: Automatic pause detection (>1s)
- Baseline calculation per audio file
- Adaptive marker triggers based on deviation thresholds

### 2. Emotion Detection
- Text-based sentiment using TextBlob
- Audio-based emotion classification
- Multi-modal emotion combination
- 7 primary emotion categories (from resonance files)

### 3. Speaker Recognition
- Automatic speaker diarization using pyannote.audio
- Speaker A, B, C labeling
- Speaker statistics and duration analysis
- Overlapped speech detection

### 4. Semantic Analysis
- ATO marker recognition system
- 63+ semantic categories based on therapeutic frameworks
- Pattern matching and correlation analysis
- Relationship mapping between messages

### 5. Output Formats
- Annotated Markdown with inline markers
- JSON sidecar files with structured data
- HTML export with color-coded speakers
- PDF export via WeasyPrint
- CSV export for data analysis

## Building and Running

### Prerequisites
- Python 3.12+
- System dependencies: `ffmpeg`, `portaudio19-dev`
- Hugging Face token (for speaker diarization)

### Installation
```bash
# System dependencies
sudo apt install python3.12 python3-pip ffmpeg portaudio19-dev

# Python packages
pip install --break-system-packages openai-whisper librosa praat-parselmouth \
    soundfile pyyaml numpy textblob nltk

# Or install from requirements
pip install -r requirements_emotion.txt
```

### Usage

#### SVT GUI (Recommended)
```bash
python3 svt.py
```

#### Direct Usage
```bash
# Process audio files with emotion analysis
python3 auto_transcriber_v4_emotion.py

# Generate super semantic analysis
python3 super_semantic_processor.py
```

## Development Conventions

### Code Structure
- Python files follow PEP 8 guidelines
- YAML files for marker definitions
- Modular design with clear component separation
- Comprehensive logging throughout

### Feature Toggles
- Prosody analysis: ±20% threshold for tempo, ±15% for pitch, ±25% for energy
- Confidence scoring with configurable thresholds
- Intelligent pipeline with quality-based model selection
- Custom marker support via YAML configuration

### Output Markers
- `[TEMPO↑/↓]`: ±20% deviation from baseline
- `[PITCH↑/↓]`: ±15% deviation from baseline
- `[ENERGY↑/↓]`: ±25% deviation from baseline
- `[PAUSE]`: Pause >1000ms
- `[ÜBERLAPPUNG Xs]`: Overlapped speech detection

## Project Status

- **Phase 1**: Prosody extraction - ✅ Complete
- **Phase 2a**: Professional layout & export - ✅ Complete
- **Phase 2b**: Speaker diarization - ✅ Complete
- **Phase 2c**: Overlapped speech detection - ✅ Complete
- **Phase 2d**: ATO-marker integration - In Progress
- **Phase 3**: Streaming & Real-time - Planned

## Key Technologies

- **OpenAI Whisper**: Speech-to-text conversion
- **Parselmouth**: Praat-based pitch extraction
- **Librosa**: Audio feature extraction
- **TextBlob**: Sentiment analysis
- **pyannote.audio**: Speaker diarization and OSD
- **PyYAML**: Configuration and marker definitions
- **Tkinter**: GUI framework

## Therapeutic Applications

The system is specifically designed for therapeutic use cases including:
- Emotional pattern analysis
- Behavioral change tracking
- Communication pattern identification
- Therapeutic intervention point detection
- Client progress monitoring
- Session content analysis

## File Format Support

- **Input**: m4a, opus, wav, mp3, flac, ogg (audio)
- **Input**: txt (WhatsApp exports), md (transcripts)
- **Output**: md, json, html, pdf, csv (all formats)