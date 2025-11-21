# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

**Working Directory**: This CLAUDE.md is located in `Super_semantic_whisper/`, which is the main working directory for all development and operations.

## Project Overview

**Semantic Voice Transcriber (SVT)** is a professional therapeutic transcription system that combines Whisper speech recognition with multi-modal analysis (prosody, emotion, semantic markers). Designed for therapeutic applications, it generates annotated transcripts with clinical insights.

**Core Components:**
- **SVT GUI** (`svt.py`): Main interface with one-click workflows
- **Transcription Pipeline** (`auto_transcriber_v4_emotion.py`): Quality-based model selection, confidence scoring
- **Prosody Engine** (`prosody_extractor.py`): Big 4 features (Tempo, Pitch, Energy, Pauses) with Parselmouth/librosa
- **Speaker System** (`speaker_diarizer.py`): pyannote.audio for multi-speaker recognition + overlapped speech detection
- **Semantic Engine** (`super_semantic_processor.py`): ATO marker detection (63+ patterns)
- **LLM Integration** (`svt_core/llm_provider/`): Multi-provider support (OpenAI, Anthropic, Google, Grok, Ollama)
- **Psychoanalysis Dashboard** (`psychoanalysis_pipeline.py` + `dashboard_generator.py`): GPT-4 emotion dynamics analysis
- **Memory System** (`Memory/`): Persistent speaker profiles with prosody baselines
- **Audit System** (`audit/`): Feature readiness gates and quality checks

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
# Run all tests with coverage
pytest -v

# Run specific test categories
pytest -v -m unit              # Unit tests only
pytest -v -m integration       # Integration tests only
pytest -v -m "not slow"        # Skip slow tests

# Run specific test files
pytest tests/test_ci_transcription.py -v
pytest tests/test_psychoanalysis_pipeline.py -v

# Run single test function
pytest tests/test_prosody_analyzer.py::test_function_name -v

# Legacy test scripts (still available)
python3 test_prosody_pipeline.py
python3 test_yaml_structure.py
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
    │   ├── audio_quality_analyzer.py → model selection (tiny/base/small/medium/large)
    │   ├── audio_preprocessor.py → noise reduction (optional)
    │   ├── speaker_diarizer.py → pyannote.audio diarization + OSD
    │   ├── prosody_extractor.py → Parselmouth (pitch) + librosa (tempo, energy)
    │   └── output_formatter.py → MD/JSON/HTML/PDF/CSV export
    ├── svt_core/
    │   ├── llm_provider/ → Multi-provider LLM abstraction
    │   │   ├── factory.py → LLMProviderFactory.create(provider_type)
    │   │   ├── providers/ → OpenAI, Anthropic, Google, Grok, Ollama
    │   │   └── manager.py → LLMProviderManager for provider switching
    │   ├── audio/diarization_cpu.py → CPU-optimized diarization
    │   ├── marker_interpreter.py → Marker interpretation logic
    │   └── ui/provider_dialog.py → LLM provider selection GUI
    ├── psychoanalysis_pipeline.py → GPT-4 emotion dynamics analysis
    ├── dashboard_generator.py → Interactive HTML dashboards (Chart.js, Cytoscape.js)
    ├── super_semantic_processor.py → ATO marker detection (63+ patterns)
    ├── ato_marker_integration.py → Curated marker set (40 markers for therapeutic use)
    ├── audit/ → Feature readiness system
    │   ├── cli.py → audit CLI commands
    │   ├── audit_runner.py → Run audits programmatically
    │   ├── feature_registry.py → Feature metadata and dependencies
    │   └── checks/ → memory_checks, speaker_view_checks, dual_marker_checks
    └── Memory/ → speaker_profiles.db (SQLite) + *.yaml (per-speaker profiles)
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

### Marker System Architecture

The project uses a multi-tier marker system based on LeanDeep 3.5:

**Local Marker Directories:**
- `VP_ATO/`: Voice-specific atomic markers (YAML) for prosody-triggered detection
- `Marker_LD3.5_SSoTh/`: 4-tier hierarchy (ATO→SEM→CLU→MEMA) with `.cursor/rules/leandeep35.mdc` specification
- `ato_detector_config_authentic.json`: Curated 40-marker set for clinical use (emotions, turning points, therapeutic patterns)

**External Integrations** (referenced in `super_semantic_processor.py`):
- `../ALL_SEMANTIC_MARKER_TXT/`: Main marker repository
- `../Marker_assist_bot/`: FRAUSAR marker management
- `../MARSAP/`: CoSD (Coherence of Self-Description) drift analysis

**Skills Integration:**
- `emotion_dynaminc-skill/`: Claude Code skill for GPT-4 UED (Utterance Emotion Dynamics) analysis
- Outputs VAD dimensions (Valence, Arousal, Dominance) + discrete emotions

All markers follow LeanDeep 3.5 schema: `id`, `frame` (signal/concept/pragmatics/narrative), `examples` (min 5), `structure` (pattern/composed_of/detect_class).

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

### LLM Provider System (`svt_core/llm_provider/`)

Multi-provider abstraction for cloud and local LLM integration:

**Supported Providers:**
- OpenAI (GPT-4, GPT-3.5)
- Anthropic (Claude Sonnet, Opus)
- Google (Gemini)
- Grok (xAI)
- Ollama (local models)

**Usage Pattern:**
```python
from svt_core.llm_provider import LLMProviderFactory

# Create provider
provider = LLMProviderFactory.create(
    provider_type="openai",
    api_key="sk-...",
    model="gpt-4-turbo-preview"
)

# Generate completion
response = provider.generate(prompt="Analyze this transcript...")
```

**Architecture:**
- `factory.py`: Provider instantiation
- `manager.py`: Runtime provider switching
- `base.py`: Abstract base class for all providers
- `providers/`: Individual provider implementations

### Audit System (`audit/`)

Feature readiness gates ensure quality before deployment:

**CLI Commands:**
```bash
python3 -m audit.cli status            # Show feature readiness
python3 -m audit.cli run memory        # Run memory checks
python3 -m audit.cli run speaker_view  # Run speaker view checks
python3 -m audit.cli report            # Generate full report
```

**Programmatic Usage:**
```python
from audit.audit_runner import AuditRunner
from audit.feature_registry import FeatureRegistry

runner = AuditRunner(FeatureRegistry())
results = runner.run_all()
print(results.summary())
```

**Check Categories:**
- `memory_checks.py`: Speaker profile integrity, prosody baseline validation
- `speaker_view_checks.py`: SpeakerConfig modes, label generation
- `dual_marker_checks.py`: Marker detection accuracy, confidence thresholds

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

**Quick Start:**
```bash
python3 svt.py  # Launch GUI
# Configure: Enable Prosody, Speaker Diarization, Memory
# Click "Transkription starten" or "Quick Test"
```

**Output Files** (in `Transkripte_LLM/`):
- `.md`: Therapeutic format with speaker headers and metadata sidebars
- `.prosody.json`: Structured prosody data (required for dashboard generation)
- `_enhanced.html`: Color-coded HTML (green=Patient, blue=Therapeut)
- `.pdf`: Professional layout for printing
- `.csv`: Data export for analysis

**Input Directory:** `Eingang/` (supports m4a, opus, wav, mp3)

### Therapeutic Transcript Format

**Key Innovation:** Metadata sidebars instead of inline markers for clean readability.

**Example:**
```markdown
### **Therapeut** | 00:05 - 00:12
Wie geht es Ihnen heute?
> **Metadaten:**
> 📊 **Prosody**: Energie ↑ (+28.0%)
> 🔍 **Marker**: ATO_AFFIRMATION
```

**Speaker Modes** (configure in `svt.py` line 50):
- `MODE_ANONYMOUS` (default): "Therapeut", "Patient"
- `MODE_LETTERS`: "Speaker A", "Speaker B"
- `MODE_NAMES`: Use actual speaker names
- `MODE_CUSTOM`: Define custom mapping dict

**40 Curated ATO Markers:**
- Emotions (14): SADNESS, ANGER, ANXIETY, JOY, FEAR, DISGUST...
- Turning Points (17): BREAKTHROUGH, INSIGHT, RESISTANCE_BREAK...
- Therapeutic (5): AFFIRMATION, DEFLECTION, DISCLOSURE...
- Psychoanalytic (4): DEFENSE_DENIAL, TRANSFERENCE_POSITIVE...

Full guide: `THERAPEUTIC_TRANSCRIPT_FORMAT.md`

### Generating Psychoanalysis Dashboard

GPT-4-powered emotion dynamics analysis with interactive visualizations.

**One-Click Workflow:**
```bash
export OPENAI_API_KEY=sk-your-key-here
python3 svt.py  # Click "🧠 Psychoanalysis Dashboard" button
# Select audio file → Auto-transcribe (if needed) → Dashboard opens in browser
```

**Dashboard Features:**
- VAD trajectory charts (Valence, Arousal, Dominance) with Chart.js
- UED metrics: Home Base, Variability, Instability, Inertia, Rise/Recovery Rates
- Marker network visualization (Cytoscape.js)
- Tri-modal turnpoint detection (Emotion + Markers + Prosody)
- 16 psychoanalytic markers (Defense, Resistance, Transference, Themes)

**Smart Caching:**
- SHA256-based transcript cache avoids redundant API calls
- Reuses existing `.prosody.json` files automatically
- Clear cache: `rm -rf cache/psychoanalysis/`

**Configuration:** `config/psychoanalysis_config.yaml` (model, thresholds, styling)

Full documentation: `PSYCHOANALYSIS_DASHBOARD.md`

### Adding New ATO Markers

Create YAML file in `VP_ATO/` following LeanDeep 3.5 schema:
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

Markers auto-load on next run. Test: `python3 test_yaml_structure.py`

### Extending Speaker Memory

**Automatic:** Profiles created on first transcription
**Manual:** `python3 initialize_person.py --name "NewSpeaker"`

Profiles stored in `Memory/speaker_profiles.db` (SQLite) + `Memory/<name>.yaml` (backup)

## Common Issues

**FFmpeg Not Found:** `sudo apt install ffmpeg` (verify: `ffmpeg -version`)

**pyannote.audio Permission Denied:** Accept Hugging Face model agreements, create token (see Speaker Diarization Setup)

**Low Transcription Quality:**
- Check audio SNR/noise in `transcription_v4_emotion.log`
- Try higher Whisper model (medium/large)
- Enable audio preprocessing in GUI

**Out of Memory (OOM) on Long Audio Files:**
SVT uses file-based incremental merge for long files (>30 minutes) to prevent OOM crashes:
- Automatic chunking at 300s (5 minutes) with 5s overlap
- Each chunk written to `/tmp/svt_chunks_*/` immediately after processing
- Peak memory = single chunk size (~500MB) instead of all chunks (~5GB+)
- If still getting OOM (exit code 137):
  - Monitor SWAP usage: `watch -n 1 free -h` (should stay < 80%)
  - Check temp directory space: `df -h /tmp` (need ~100MB for chunk files)
  - Review detailed guide: `docs/MEMORY_OPTIMIZATION.md`
  - Increase chunk duration to reduce chunk count: edit `CHUNK_DURATION` in `audio_chunker.py`

**Memory Profile Not Updating:**
- Check write permissions on `Memory/` directory
- Validate YAML: `python3 test_yaml_structure.py`

**Stale Python Cache:**
```bash
find . -name "*.pyc" -delete
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null
```

## Current Development Status

**Phase 2c (Complete):** Prosody extraction, professional formats, speaker diarization, OSD, intelligent pipeline, psychoanalysis dashboard, UED analysis, CI/CD

**Phase 2d (In Progress):** ATO marker integration with prosody triggers, real-time marker detection, ATO→SEM→CLU→MEMA hierarchy refinement

**Phase 3 (Planned):** Live streaming transcription, real-time prosody visualization, WebSocket API, multi-session comparative analysis

## Key Implementation Details

**Logging:**
- Primary: `transcription_v4_emotion.log`
- Quality warnings and confidence scores per segment

**Git Workflow:**
- `main`: Stable releases
- `feat/*`: Feature branches (current: `feat/professional-quality-enhancement`)
- Commit prefixes: `feat:`, `fix:`, `docs:`, `test:`, `refactor:`

**CI/CD:**
- `.github/workflows/test.yml`: Main test suite
- `.github/workflows/psychoanalysis-ci.yml`: Dashboard pipeline tests
- `.github/workflows/feature_audit.yml`: Readiness gate checks

**Performance Considerations:**
- Whisper model selection based on audio quality (SNR, duration, energy)
- CPU-optimized diarization in `svt_core/audio/diarization_cpu.py`
- Transcript caching for psychoanalysis (SHA256-based)
- Prosody analysis runs per-segment (3-10s aligned with Whisper)
