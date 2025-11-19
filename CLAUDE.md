# CLAUDE.md

**Last Updated:** 2025-11-19 | **Verified against commit:** 75fdfbbc

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

**Working Directory**: This CLAUDE.md is located in `Semantic_Voice_Transcriber/`, which is the main working directory for all development and operations.

## Project Overview

**Semantic Voice Transcriber (SVT)** is a professional therapeutic transcription system that combines state-of-the-art speech recognition with advanced prosody analysis, emotion detection, and semantic marker recognition. Designed for therapeutic applications, it provides deep insights into spoken communication through multi-modal analysis.

The system consists of interconnected components:
- **SVT Core**: Professional transcription GUI with one-click workflow
- **Transcription Engine**: Whisper-based STT with intelligent quality-based model selection
- **Prosody Analysis**: Big 4 features (Tempo, Pitch, Energy, Pauses) with baseline deviation detection
- **Speaker Diarization**: Automatic multi-speaker recognition with overlapped speech detection
- **Emotion Detection**: Multi-modal analysis combining audio features and text sentiment
- **Semantic Processing**: ATO marker system for behavioral and linguistic pattern recognition
- **Memory System**: Persistent speaker profiles with learning capabilities

## Core Commands

### Main Entry Points

```bash
# SVT GUI - Professional transcription interface (RECOMMENDED)
python3 svt.py

# Legacy/Alternative interfaces
python3 auto_transcriber_v4_emotion.py  # V4 with emotion analysis
python3 start_super_semantic.py          # Interactive launcher
python3 super_semantic_gui.py            # Semantic analysis GUI
```

### Testing

```bash
# Run all prosody and integration tests
python3 test_prosody_analyzer.py
python3 test_prosody_pipeline.py
python3 test_confidence_scoring.py
python3 test_intelligent_pipeline_integration.py
python3 test_transcriber_osd_integration.py
python3 test_output_formatter_osd.py

# Transcription tests
python3 test_transcription.py

# Quick validation
python3 test_initialize_person.py
python3 test_yaml_structure.py

# Run a single test
python3 -m pytest test_prosody_analyzer.py::test_function_name -v

# CI/CD tests (fast tests without real audio/API calls)
python3 -m pytest tests/test_ci_transcription.py -v
python3 -m pytest tests/test_ci_pipeline.py -v
python3 -m pytest tests/test_ci_gpt_integration.py -v

# Psychoanalysis Dashboard tests
python3 -m pytest tests/test_psychoanalysis_pipeline.py -v
python3 -m pytest tests/test_dashboard_generator.py -v
python3 -m pytest tests/test_e2e_psychoanalysis.py -v
```

### Installation

```bash
# System dependencies (Ubuntu/Debian)
sudo apt install python3.12 python3-pip ffmpeg portaudio19-dev python3-tk

# Core dependencies
pip install -r requirements.txt

# Emotion analysis features
pip install -r requirements_emotion.txt

# Prosody analysis (critical for SVT)
pip install praat-parselmouth librosa soundfile
```

### Speaker Diarization Setup

Speaker diarization requires a Hugging Face token:

1. Create account at https://huggingface.co/join
2. Accept user agreements:
   - https://huggingface.co/pyannote/segmentation-3.0
   - https://huggingface.co/pyannote/speaker-diarization-3.1
3. Create read token at https://huggingface.co/settings/tokens
4. Create `.env` file:
   ```bash
   HF_TOKEN=hf_YourTokenHere
   ```

See `SPEAKER_DIARIZATION.md` for details.

## Architecture

### Processing Pipeline

```
Audio Input (m4a, opus, wav, mp3)
    ↓
[Audio Quality Analysis] → Model Selection (tiny/base/small/medium/large)
    ↓
[Audio Preprocessing] → Noise reduction, normalization (optional)
    ↓
[Whisper Transcription] → Segments with timestamps + confidence scores
    ↓
[Speaker Diarization] → Speaker A, B, C labels + overlap detection
    ↓
[Prosody Extraction] → Tempo, Pitch, Energy, Pauses per segment
    ↓
[Baseline Calculation] → Global means for deviation detection
    ↓
[Emotion Analysis] → TextBlob sentiment + audio features
    ↓
[ATO Marker Detection] → Semantic pattern matching (63+ markers)
    ↓
[Memory Update] → Update speaker profiles with prosody patterns
    ↓
[Output Formatting] → MD, JSON, HTML, PDF, CSV with markers
```

### Core Module Interaction

```
svt.py (GUI)
    ├── auto_transcriber_v4_emotion.py (orchestrates pipeline)
    │   ├── audio_quality_analyzer.py (SNR, quality metrics)
    │   ├── audio_preprocessor.py (noise reduction)
    │   ├── speaker_diarizer.py (pyannote.audio)
    │   ├── prosody_extractor.py (Parselmouth, librosa)
    │   └── output_formatter.py (multi-format export)
    ├── super_semantic_processor.py (ATO marker detection)
    └── Memory/ (speaker profiles, SQLite DB)
```

### Key Components

**Transcription Layer** (`auto_transcriber_v4_emotion.py`)
- Whisper STT with multiple model sizes
- Intelligent pipeline: quality analysis → model selection → transcription
- Confidence scoring from Whisper's avg_logprob and no_speech_prob
- Automatic language detection

**Prosody Extraction** (`prosody_extractor.py`)
- Parselmouth (Praat): F0 pitch extraction with jitter/shimmer
- Librosa: Tempo (WPM), energy (RMS/dB), audio features
- Per-segment analysis aligned with Whisper segments (3-10s)
- Global baseline calculation for deviation detection
- Threshold-based marker triggering: Tempo ±20%, Pitch ±15%, Energy ±25%, Pause >1s

**Speaker System** (`speaker_diarizer.py`)
- pyannote.audio 3.1 for automatic speaker segmentation
- Overlapped Speech Detection (OSD) with duration tracking
- Speaker labels without name assignment (A, B, C...)
- Integration with prosody and transcription pipelines

**Output System** (`output_formatter.py`)
- Annotated Markdown: Human-readable with inline markers
  - `[TEMPO↑]` / `[TEMPO↓]`: ±20% deviation
  - `[PITCH↑]` / `[PITCH↓]`: ±15% deviation
  - `[ENERGY↑]` / `[ENERGY↓]`: ±25% deviation
  - `[PAUSE]`: >1000ms silence
  - `[ÜBERLAPPUNG Xs]`: Overlapped speech duration
  - `[UNSICHER:score]`: Low confidence segments
- JSON sidecar: Structured prosody data for system processing
- HTML/PDF: Color-coded speakers with professional layout
- CSV: Data export for analysis

**Memory System** (`Memory/*.yaml`)
- Persistent speaker profiles with prosody patterns (pitch/tempo/energy averages)
- Speech statistics (avg_sentence_length, sentiment ratios)
- Topic tracking and characteristics
- Last 50 interactions with timestamps
- Running averages updated per transcription

**Semantic Engine** (`super_semantic_processor.py`)
- 63+ ATO (Atomic) marker categories in YAML
- Pattern matching and correlation analysis
- Integration with external marker systems:
  - `../ALL_SEMANTIC_MARKER_TXT/`: Main marker repository
  - `../Marker_assist_bot/`: FRAUSAR marker management
  - `../MARSAP/`: CoSD drift analysis
- Relationship mapping between messages

### Directory Structure

```
Super_semantic_whisper/
├── svt.py                          # Main GUI entry point
├── auto_transcriber_v4_emotion.py  # V4 transcription engine
├── prosody_extractor.py            # Prosody analysis (Phase 1)
├── speaker_diarizer.py             # Speaker diarization + OSD
├── output_formatter.py             # Multi-format output
├── audio_quality_analyzer.py       # Quality analysis for model selection
├── audio_preprocessor.py           # Audio preprocessing
├── audio_chunker.py                # Audio segmentation utilities
├── super_semantic_processor.py     # Semantic analysis engine
│
├── Eingang/                        # INPUT: Audio files (organized by speaker)
│   └── Patient/                    # Speaker-specific folders
├── Transkripte_LLM/                # OUTPUT: Transcripts (MD, JSON, HTML, PDF, CSV)
├── Memory/                         # Speaker profiles (YAML + SQLite)
│   ├── speaker_profiles.db         # SQLite speaker database
│   ├── Unknown.yaml                # Unknown speaker profile
│   └── *.yaml                      # Individual speaker profiles
│
├── VP_ATO/                         # Atomic Voice Markers (YAML)
├── Marker_LD3.5_SSoTh/             # 4-Tier marker system (LeanDeep 3.5)
│   └── .cursor/rules/              # Cursor IDE configuration (leandeep35.mdc)
├── TextBlob/                       # Local TextBlob installation
├── emotion_dynaminc-skill/         # UED emotion dynamics analysis skill
│   └── emotion-dynamics-deep-insight/  # Claude Code skill for GPT-4 integration
├── Emotion_marker_psychoanalysis/  # Psychoanalysis dashboard output
│   └── output-dashboard/           # Generated HTML dashboards
├── config/                         # Configuration files
│   └── psychoanalysis_config.yaml  # Dashboard and API settings
├── requirements.txt                # Core dependencies
└── requirements_emotion.txt        # Emotion analysis dependencies
```

### Marker Directory Relationships

The project integrates multiple marker systems:

1. **VP_ATO/**: Voice-specific atomic markers (YAML format) for prosody-triggered detection
2. **Marker_LD3.5_SSoTh/**: LeanDeep 3.5 framework with 4-tier hierarchy (ATO→SEM→CLU→MEMA)
   - Contains `.cursor/rules/leandeep35.mdc` with complete framework specification
3. **External integrations** (referenced in `super_semantic_processor.py`):
   - `../ALL_SEMANTIC_MARKER_TXT/`: Main marker repository
   - `../Marker_assist_bot/`: FRAUSAR marker management system
   - `../MARSAP/`: CoSD (Coherence of Self-Description) drift analysis
4. **emotion_dynaminc-skill/**: Claude Code skill for GPT-4-based UED analysis
   - Integrates with Psychoanalysis Dashboard feature
   - Outputs structured JSON with VAD dimensions and discrete emotions

All marker systems follow the LeanDeep 3.5 JSON schema with `id`, `frame`, `examples` (min 5), and structure fields.
```

## Important Technical Details

### LeanDeep 3.5 Marker System

The project uses the LeanDeep 3.5 framework with a 4-tier marker hierarchy:
- **ATO_** (Atomic): Primitive signals (tokens, emojis, regex patterns)
- **SEM_** (Semantic): Combinations of 2+ ATOs forming micro-patterns
- **CLU_** (Cluster): Thematic aggregations of SEMs over defined windows
- **MEMA_** (Meta-Analysis): Dynamic patterns emerging from multiple CLUs

Key concepts:
- **Intuition Markers**: CLU_INTUITION_* markers track provisional → confirmed → decayed states
- **Resonance Framework 2.0 (RF2.0)**: Contextualizes markers by developmental stages (L1:STONE → L8:COSMOS)
- **Matrix Rules**: RF_BRIDGE module combines level × marker-type × time × intensity

All markers follow JSON schema with `id`, `frame` (signal/concept/pragmatics/narrative), `examples` (min 5), and structure (`pattern`/`composed_of`/`detect_class`).

See `.cursor/rules/leandeep35.mdc` for full specification.

### Confidence Score Calculation

Whisper provides `avg_logprob` (negative) and `no_speech_prob`. Conversion to 0-1 confidence:
```python
confidence = exp(avg_logprob) * (1 - no_speech_prob)
```
Segments with confidence < 0.5 are marked as `[UNSICHER:score]`.

### Prosody Marker Thresholds

Configurable in `prosody_extractor.py`:
- **TEMPO_THRESHOLD**: ±20% deviation from baseline
- **PITCH_THRESHOLD**: ±15% deviation from baseline
- **ENERGY_THRESHOLD**: ±25% deviation from baseline
- **PAUSE_THRESHOLD**: 1000ms (1 second)

### Memory Profile Structure

YAML profiles include:
```yaml
prosody_patterns:
  pitch_profile:
    mean_pitch: 147.8          # Hz
    pitch_variability: 19.4    # Std dev
    sample_count: 15
  tempo_profile:
    mean_bpm: 118.5
    mean_speech_rate: 4.3      # Syllables/sec
  energy_profile:
    mean_energy: 0.045         # RMS
    energy_variability: 0.012
    mean_dynamic_range: 0.28

statistics:
  avg_sentence_length: 15.3
  sentiment: {positive: 42, negative: 8, ratio: 5.25}

topics: {technology: 15, business: 8, personal: 23}
characteristics: [technisch_orientiert, bedächtig, präzise]
interactions: [...]  # Last 50 transcriptions
```

### Audio File Naming Convention

WhatsApp audio: `WhatsApp Audio YYYY-MM-DD at HH.MM.SS.opus`

Output format: `YYYY-MM-DD_HH-MM-SS_speaker_originalname_transkript.md`

Timestamp extracted and used for metadata and temporal analysis.

### Whisper Model Selection

Intelligent pipeline analyzes audio quality and selects model:
- **tiny**: 39M params, fast, lower accuracy
- **base**: 74M params, balanced
- **small**: 244M params (default for testing)
- **medium**: 769M params, high accuracy
- **large**: 1550M params, best quality

Selection based on:
- SNR (Signal-to-Noise Ratio)
- Audio duration
- Zero-crossing rate
- Energy distribution

## Development Workflows

### Processing Audio Files

1. Place audio in `Eingang/Patient/` (or speaker-specific folder)
2. Launch SVT GUI: `python3 svt.py`
3. Configure features:
   - Prosody Analysis (Big 4: Tempo, Pitch, Energy, Pauses)
   - Emotion Detection (TextBlob sentiment)
   - Speaker Diarization (pyannote.audio)
   - Memory Updates (speaker profiles)
4. Click "Transkription starten" (batch) or "Quick Test" (first file only)
5. Output appears in `Transkripte_LLM/`:
   - `.md` - **NEW** Therapeutic format with speaker headers and metadata sidebar
   - `.prosody.json` - Structured prosody data
   - `.html` - Legacy HTML (color-coded speakers)
   - `_enhanced.html` - **NEW** Therapeutic HTML (green=Patient, blue=Therapeut)
   - `.pdf` - Professional layout
   - `.csv` - Data export

### Therapeutic Transcript Format (New in v1.0)

**Speaker Labels Now Visible:**
```markdown
### **Therapeut** | 00:05 - 00:12

Wie geht es Ihnen heute?

> **Metadaten:**
> 📊 **Prosody**: Energie ↑ (+28.0%)
```

**Key Features:**
- ✅ **Speaker headers**: Clear "Therapeut" / "Patient" labels (configurable)
- ✅ **Metadata sidebar**: Prosody and ATO markers organized below each utterance
- ✅ **Clean text**: No inline markers cluttering the transcript
- ✅ **Enhanced HTML**: Color-coded speakers with hover effects
- ✅ **ATO markers**: Automatic detection of 40 curated semantic patterns

**Speaker Modes** (edit `svt.py` line 50):
- `MODE_ANONYMOUS` (default): "Therapeut", "Patient"
- `MODE_LETTERS`: "Speaker A", "Speaker B"
- `MODE_NAMES`: Use actual names
- `MODE_CUSTOM`: Define custom mapping

**ATO Markers Detected:**
- Emotions: SADNESS, ANGER, ANXIETY, JOY
- Turning Points: BREAKTHROUGH, INSIGHT, RESISTANCE_BREAK
- Therapeutic: AFFIRMATION, DEFLECTION, DISCLOSURE

**See:** `THERAPEUTIC_TRANSCRIPT_FORMAT.md` for comprehensive user guide

### Generating Psychoanalysis Dashboard

**Psychoanalysis Dashboard** provides GPT-4-powered emotion dynamics analysis with interactive visualizations.

#### One-Click Workflow (Recommended)

1. **Set OpenAI API key** (prerequisite):
   ```bash
   export OPENAI_API_KEY=sk-your-key-here
   # Or create .env file with OPENAI_API_KEY=sk-your-key-here
   ```

2. **Launch SVT GUI**: `python3 svt.py`

3. **Click "🧠 Psychoanalysis Dashboard" button**

4. **Select audio file** in file dialog (m4a, opus, wav, mp3, etc.)

5. **Automatic workflow**:
   - System checks for existing `.prosody.json` transcript
   - **If exists**: Reuses transcript (skips transcription)
   - **If not**: Transcribes audio asynchronously with **prosody forced ON**
   - Runs psychoanalysis pipeline with GPT-4-Turbo
   - Generates interactive HTML dashboard
   - **Auto-opens in browser**

6. **Dashboard contents**:
   - Annotated transcript with emotion states
   - VAD trajectory charts (Valence, Arousal, Dominance)
   - Discrete emotion frequency analysis
   - UED metrics (Home Base, Variability, Instability, Inertia, Rise/Recovery Rates)
   - Marker network visualization (Cytoscape.js)
   - Therapeutic turning point annotations

**Key Features**:
- ✅ **Smart caching**: Reuses existing transcripts automatically
- ✅ **Async processing**: Non-blocking GUI during transcription
- ✅ **Prosody enforcement**: Always includes prosody data (required for dashboard)
- ✅ **Tri-modal turnpoint detection**: Emotion + Markers + Prosody

**Configuration**: Edit `config/psychoanalysis_config.yaml` to customize:
- OpenAI model and parameters (`gpt-4-turbo-preview` by default)
- Turnpoint detection thresholds (valence, arousal, prosody pauses)
- Marker weights and categories
- Dashboard styling and output directory

**Cache System**:
- Transcript-based caching (SHA256 hash)
- Avoids redundant API calls
- See `psychoanalysis_cache.py` for details
- Manual clear: `rm -rf cache/psychoanalysis/`

**See**: `PSYCHOANALYSIS_DASHBOARD.md` for comprehensive usage guide

### Adding New ATO Markers

1. Create YAML file: `ATO_NEW_MARKER.yaml` in project root or `VP_ATO/`
2. Follow LeanDeep 3.5 schema:
   ```yaml
   id: ATO_YOUR_MARKER
   frame:
     signal: "regex pattern or token"
     concept: "What it represents"
     pragmatics: "How it's used"
     narrative: "Why it matters"
   examples: ["example1", "example2", ...]  # Min 5 required
   pattern: "detection logic"
   ```
3. Markers auto-loaded by semantic processor on next run
4. Test with: `python3 test_yaml_structure.py`

### Running Semantic Analysis

```bash
# GUI mode (recommended)
python3 super_semantic_gui.py

# Programmatic
python3 super_semantic_processor.py --input transcripts/ --marker-set All_Markers
```

### Extending Speaker Memory

New speaker profiles created automatically on first transcription. To manually initialize:
```bash
python3 initialize_person.py --name "NewSpeaker"
```

Profiles stored in:
- `Memory/speaker_profiles.db` (SQLite)
- `Memory/<speaker_name>.yaml` (YAML backup)

## Common Issues

### FFmpeg Not Found
Install FFmpeg: `sudo apt install ffmpeg` or `brew install ffmpeg`
Verify: `ffmpeg -version`

### pyannote.audio Permission Denied
Accept Hugging Face model agreements and create token (see Speaker Diarization Setup above)

### Low Transcription Quality
- Check audio quality (SNR, noise levels)
- Try higher Whisper model (medium/large)
- Enable audio preprocessing
- Review `transcription_v4_emotion.log` for quality warnings

### Memory Profile Not Updating
- Verify write permissions on `Memory/` directory
- Check YAML syntax with `python3 test_yaml_structure.py`
- Review logs for serialization errors

## Current Development Status

**Phase 2c Complete** ✅
- ✅ Prosody extraction (Big 4 features)
- ✅ Professional output formats (MD, JSON, HTML, PDF, CSV)
- ✅ Speaker diarization with pyannote.audio
- ✅ Overlapped speech detection (OSD)
- ✅ Intelligent pipeline with quality-based model selection
- ✅ **Psychoanalysis Dashboard with GPT-4 integration** (NEW)
- ✅ **Interactive HTML dashboards with Chart.js and Cytoscape.js** (NEW)
- ✅ **UED (Utterance Emotion Dynamics) analysis** (NEW)
- ✅ **CI/CD test suite for pipeline validation** (NEW)

**Phase 2d In Progress** 🔄
- ATO marker integration with prosody triggers
- Real-time marker detection during transcription
- ATO → SEM → CLU → MEMA hierarchy refinement
- GUI integration for speaker editing
- Therapeutic turning point detection enhancement

**Phase 3 Planned** 📋
- Live streaming transcription
- Real-time prosody visualization
- WebSocket API for external tools
- Real-time marker display
- Multi-session comparative analysis

## Logging

- `transcription_v4_emotion.log`: Main transcription log
- `transcription.log`: Legacy V3 log
- Console output with timestamps for all operations
- Quality warnings and confidence scores logged per segment

## Git Workflow

Current branch structure:
- `main`: Stable releases
- `feat/*`: Feature branches (current: `feat/professional-quality-enhancement`)

When making commits:
1. Stage changes: `git add <files>`
2. Commit with descriptive message: `git commit -m "feat: description"`
3. Push to remote: `git push origin <branch-name>`

Commit prefixes:
- `feat:` New features
- `fix:` Bug fixes
- `docs:` Documentation changes
- `test:` Test additions/modifications
- `refactor:` Code restructuring
