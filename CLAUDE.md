# CLAUDE.md

**Last Updated:** 2025-11-20 | **Verified against commit:** 39ed3ff

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
- **LLM Integration**: Dual provider support (OpenAI GPT-4 + FREE local Ollama)
- **Health Monitoring**: Real-time system status and provider health checks
- **Audit System**: Feature readiness tracking and quality assurance

### Codebase Statistics

- **164** Python files (17,509 lines in root)
- **58** Test files (42 in tests/, 16 in root)
- **57** Documentation files
- **37** Marker definition files (18 ATO, 3 SEM, 16 in VP_ATO/)
- **5** Audio format support (.opus, .m4a, .wav, .mp3, .ogg)
- **5** Whisper model sizes (tiny → large)
- **2** LLM providers (OpenAI, Ollama)
- **4** Prosody features ("Big 4": Tempo, Pitch, Energy, Pauses)
- **7** Output formats (MD, JSON, HTML, Enhanced HTML, PDF, CSV, Dashboard)

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
    ├── svt_core/ (modular architecture)
    │   ├── health_check.py (system status monitoring)
    │   ├── llm_provider/ (provider abstraction)
    │   │   ├── factory.py (build providers)
    │   │   ├── manager.py (provider management)
    │   │   ├── local_ollama.py (FREE local LLM)
    │   │   └── providers/ (OpenAI, Anthropic, etc.)
    │   ├── config/settings.py (persistent configuration)
    │   └── ui/provider_dialog.py (settings GUI)
    │
    ├── auto_transcriber_v4_emotion.py (orchestrates pipeline)
    │   ├── audio_quality_analyzer.py (SNR, quality metrics)
    │   ├── audio_preprocessor.py (noise reduction)
    │   ├── speaker_diarizer.py (pyannote.audio)
    │   ├── prosody_extractor.py (Parselmouth, librosa)
    │   └── output_formatter.py (multi-format export)
    │
    ├── psychoanalysis_pipeline.py (emotion dynamics)
    │   ├── psychoanalysis_api.py (OpenAI GPT-4)
    │   ├── psychoanalysis_api_ollama.py (local Ollama)
    │   ├── psychoanalysis_cache.py (transcript caching)
    │   └── dashboard_generator.py (HTML dashboards)
    │
    ├── ato_marker_integration.py (semantic markers)
    │   └── super_semantic_processor.py (ATO/SEM detection)
    │
    ├── audit/ (feature readiness system)
    │   ├── feature_registry.py (feature tracking)
    │   ├── audit_runner.py (run audits)
    │   └── report_builder.py (generate reports)
    │
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

**LLM Provider System** (`svt_core/llm_provider/`)
- **Provider Abstraction**: Unified interface for all LLM backends
  - `LLMProvider` base class with `generate()`, `health_check()`, and `describe()` methods
  - `LLMResponse` normalized response format (text, usage, metadata)
- **Provider Factory**: Dynamic provider instantiation via `build_default_manager()`
- **Multi-Provider Support**:
  - **Ollama (Local)**: FREE, privacy-preserving local LLM (qwen2.5-coder:7b)
  - **OpenAI**: GPT-4-Turbo for psychoanalysis dashboards
  - **Anthropic**: Future support for Claude integration
  - **Dummy**: Testing provider for CI/CD
- **Provider Manager**: Session-based provider lifecycle management
- **Settings Store**: Persistent configuration with `ProviderProfile` serialization
- **GUI Integration**: `ProviderDialog` for user-friendly provider configuration

**Health Check System** (`svt_core/health_check.py`)
- Real-time system status monitoring
- Provider health verification (Ollama connectivity, API key validation)
- Status levels: `ok` (green), `warn` (yellow), `error` (red)
- Integrated into SVT GUI with visual indicators
- Automatic checks on startup and provider changes

**Audit System** (`audit/`)
- **Feature Registry**: Tracks implementation status of all features
- **Readiness Scoring**: Quantifies feature completeness (0-100)
- **Audit Runner**: Automated feature verification
- **Report Builder**: Generates comprehensive audit reports
- **CLI Interface**: `python3 -m audit.cli` for command-line audits
- **Use Cases**: Quality assurance, documentation verification, release readiness

### Directory Structure

```
Semantic_Voice_Transcriber/
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
├── svt_core/                       # Core modular architecture (NEW)
│   ├── audio/                      # Audio processing modules
│   │   └── diarization_cpu.py      # CPU-optimized speaker diarization
│   ├── llm_provider/               # LLM provider abstraction layer
│   │   ├── base.py                 # LLMProvider interface & LLMResponse
│   │   ├── factory.py              # Provider factory and builder
│   │   ├── manager.py              # Provider manager
│   │   ├── local_ollama.py         # Local Ollama integration (FREE)
│   │   └── providers/              # Cloud provider implementations
│   ├── config/                     # Configuration management
│   │   └── settings.py             # Settings store and profiles
│   ├── ui/                         # UI components
│   │   └── provider_dialog.py      # Provider settings dialog
│   ├── tools/                      # Utility tools
│   └── health_check.py             # System health monitoring
│
├── audit/                          # Feature readiness audit system
│   ├── audit_runner.py             # Audit execution engine
│   ├── feature_registry.py         # Feature tracking registry
│   ├── readiness.py                # Readiness scoring
│   ├── report_builder.py           # Report generation
│   ├── cli.py                      # CLI interface
│   ├── checks/                     # Feature check modules
│   └── schemas/                    # Validation schemas
│
├── Eingang/                        # INPUT: Audio files (organized by speaker)
│   └── Patient/                    # Speaker-specific folders
├── Transkripte_LLM/                # OUTPUT: Transcripts (MD, JSON, HTML, PDF, CSV)
├── Memory/                         # Speaker profiles (YAML + SQLite)
│   ├── speaker_profiles.db         # SQLite speaker database
│   ├── Unknown.yaml                # Unknown speaker profile
│   └── *.yaml                      # Individual speaker profiles
│
├── VP_ATO/                         # Atomic Voice Markers (YAML) - 16 files
├── ATO_*.yaml                      # Root-level ATO markers (18 files)
├── SEM_*.yaml                      # Root-level SEM markers (3 files)
├── Marker_LD3.5_SSoTh/             # 4-Tier marker system (LeanDeep 3.5)
│   └── .cursor/rules/              # Cursor IDE configuration (leandeep35.mdc)
├── config/                         # Configuration files
│   └── psychoanalysis_config.yaml  # Dashboard and API settings (OpenAI/Ollama)
├── docs/                           # Documentation (57 files)
│   ├── architecture/               # Architecture documentation
│   ├── plans/                      # Planning documents
│   └── reviews/                    # Code reviews
├── tests/                          # Test suite (42 test files)
│   └── affect/                     # Emotion/affect tests
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

**Psychoanalysis Dashboard** provides LLM-powered emotion dynamics analysis with interactive visualizations. Supports both **OpenAI GPT-4** (cloud) and **Ollama** (FREE local LLM).

#### Provider Selection

**Option 1: Ollama (FREE, Recommended)**
```bash
# Install Ollama (one-time setup)
curl -fsSL https://ollama.com/install.sh | sh

# Download model (one-time)
ollama pull qwen2.5-coder:7b

# Start Ollama server
ollama serve
```

**Option 2: OpenAI (Cloud API)**
```bash
export OPENAI_API_KEY=sk-your-key-here
# Or create .env file with OPENAI_API_KEY=sk-your-key-here
```

Configure provider in `config/psychoanalysis_config.yaml`:
```yaml
provider: ollama  # or "openai"
```

Or use GUI: **Einstellungen → Provider-Einstellungen**

#### One-Click Workflow

1. **Launch SVT GUI**: `python3 svt.py`

2. **Verify system status**: Check health indicator (top-right, should be green)

3. **Click "🧠 Psychoanalysis Dashboard" button**

**Dashboard Features:**
- VAD trajectory charts (Valence, Arousal, Dominance) with Chart.js
- UED metrics: Home Base, Variability, Instability, Inertia, Rise/Recovery Rates
- Marker network visualization (Cytoscape.js)
- Tri-modal turnpoint detection (Emotion + Markers + Prosody)
- 16 psychoanalytic markers (Defense, Resistance, Transference, Themes)

5. **Automatic workflow**:
   - System checks for existing `.prosody.json` transcript
   - **If exists**: Reuses transcript (skips transcription)
   - **If not**: Transcribes audio asynchronously with **prosody forced ON**
   - Runs psychoanalysis pipeline with configured LLM provider
   - Generates interactive HTML dashboard
   - **Auto-opens in browser**

**Configuration:** `config/psychoanalysis_config.yaml` (model, thresholds, styling)

**Key Features**:
- ✅ **Dual provider support**: OpenAI (cloud) or Ollama (local, FREE)
- ✅ **Smart caching**: Reuses existing transcripts automatically
- ✅ **Async processing**: Non-blocking GUI during transcription
- ✅ **Prosody enforcement**: Always includes prosody data (required for dashboard)
- ✅ **Tri-modal turnpoint detection**: Emotion + Markers + Prosody
- ✅ **Privacy mode**: Local processing with Ollama (no data leaves machine)

**Configuration**: Edit `config/psychoanalysis_config.yaml` to customize:
- Provider selection: `ollama` or `openai`
- OpenAI model and parameters (`gpt-4-turbo-preview` by default)
- Ollama model and endpoint (`qwen2.5-coder:7b` by default)
- Turnpoint detection thresholds (valence, arousal, prosody pauses)
- Marker weights and categories
- Dashboard styling and output directory

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

### Running Feature Audits

The audit system tracks feature implementation status and generates readiness reports:

```bash
# Run full audit
python3 -m audit.cli

# Run specific audit module
python3 -m audit.audit_runner

# Generate readiness report
python3 -m audit.report_builder
```

Features tracked:
- Transcription accuracy and confidence scoring
- Prosody extraction completeness
- Speaker diarization functionality
- Output format generation
- Memory system persistence
- LLM provider health
- GUI component availability

### Configuring LLM Providers

**Via GUI**:
1. Launch SVT: `python3 svt.py`
2. Menu: **Einstellungen → Provider-Einstellungen**
3. Select provider (Ollama or OpenAI)
4. Configure settings (API key, model, endpoint)
5. Save and restart

**Via Configuration File**:
Edit `config/psychoanalysis_config.yaml`:
```yaml
provider: ollama  # or "openai"

ollama:
  base_url: http://localhost:11434
  model: qwen2.5-coder:7b
  temperature: 0.7

openai:
  api_key: ${OPENAI_API_KEY}
  model: gpt-4-turbo-preview
  temperature: 0.3
```

**Via Environment Variables**:
```bash
# OpenAI
export OPENAI_API_KEY=sk-your-key-here

# Ollama (if non-default endpoint)
export OLLAMA_BASE_URL=http://custom-host:11434
```

## Common Issues

**Phase 2d (In Progress):** ATO marker integration with prosody triggers, real-time marker detection, ATO→SEM→CLU→MEMA hierarchy refinement

**Phase 3 (Planned):** Live streaming transcription, real-time prosody visualization, WebSocket API, multi-session comparative analysis

## Key Implementation Details

**Logging:**
- Primary: `transcription_v4_emotion.log`
- Quality warnings and confidence scores per segment

### Ollama Connection Failed
**Symptoms**: Health indicator shows red, "Ollama not available" error
**Solutions**:
1. Install Ollama: `curl -fsSL https://ollama.com/install.sh | sh`
2. Start Ollama server: `ollama serve`
3. Download model: `ollama pull qwen2.5-coder:7b`
4. Check server: `curl http://localhost:11434/api/version`
5. Verify firewall allows port 11434

### OpenAI API Key Invalid
**Symptoms**: Health indicator shows red, "OpenAI API key not set" error
**Solutions**:
1. Get API key from https://platform.openai.com/api-keys
2. Set environment variable: `export OPENAI_API_KEY=sk-your-key`
3. Or create `.env` file with `OPENAI_API_KEY=sk-your-key`
4. Restart SVT GUI
5. Use **Einstellungen → Provider-Einstellungen** to verify

### Psychoanalysis Dashboard Empty/Errors
**Symptoms**: Dashboard generates but missing charts or analysis
**Solutions**:
1. Verify prosody data exists: Check for `.prosody.json` file
2. Check LLM provider health (top-right indicator)
3. Review console logs for API errors
4. Try alternative provider (Ollama ↔ OpenAI)
5. Clear cache: `rm -rf cache/psychoanalysis/`
6. Check `config/psychoanalysis_config.yaml` settings

## Current Development Status

**Phase 2c Complete** ✅
- ✅ Prosody extraction (Big 4 features)
- ✅ Professional output formats (MD, JSON, HTML, PDF, CSV)
- ✅ Speaker diarization with pyannote.audio
- ✅ Overlapped speech detection (OSD)
- ✅ Intelligent pipeline with quality-based model selection
- ✅ **Psychoanalysis Dashboard with dual provider support** (OpenAI + Ollama)
- ✅ **Interactive HTML dashboards with Chart.js and Cytoscape.js**
- ✅ **UED (Utterance Emotion Dynamics) analysis**
- ✅ **CI/CD test suite for pipeline validation** (58 test files)
- ✅ **LLM Provider abstraction layer** (svt_core/llm_provider/)
- ✅ **Health monitoring system** (real-time provider status)
- ✅ **Feature audit system** (readiness tracking)
- ✅ **Modular architecture** (svt_core/ refactoring)
- ✅ **Settings persistence** (provider profiles, user preferences)
- ✅ **Ollama integration** (FREE local LLM alternative)

**Phase 2d In Progress** 🔄
- ATO marker integration with prosody triggers
- Real-time marker detection during transcription
- ATO → SEM → CLU → MEMA hierarchy refinement
- Therapeutic turning point detection enhancement
- Multi-provider LLM support expansion (Anthropic Claude, Azure OpenAI)
- Cross-platform installer improvements

**Phase 3 Planned** 📋
- Live streaming transcription
- Real-time prosody visualization
- WebSocket API for external tools
- Real-time marker display
- Multi-session comparative analysis
- Advanced speaker memory with learning curves
- Prosody-aware voice activity detection (VAD)

## Logging

- `transcription_v4_emotion.log`: Main transcription log
- `transcription.log`: Legacy V3 log
- Console output with timestamps for all operations
- Quality warnings and confidence scores logged per segment

## Git Workflow

Current branch structure:
- `main`: Stable releases (latest: 39ed3ff)
- `feat/*`: Feature branches (merged into main)
- `claude/*`: AI assistant working branches (active development)

**Active branches**:
- `claude/claude-md-mi7u4wp2t4d8ks0w-01XAdGzQSnryFHvfuNoM5CLg`: Current session

When making commits:
1. Stage changes: `git add <files>`
2. Commit with descriptive message: `git commit -m "feat: description"`
3. Push to remote: `git push -u origin <branch-name>`

Commit prefixes:
- `feat:` New features
- `fix:` Bug fixes
- `docs:` Documentation changes (include verification banner)
- `test:` Test additions/modifications
- `refactor:` Code restructuring
- `chore:` Maintenance tasks (deps, config, etc.)

**Documentation Verification**:
All documentation files should include verification banners:
```markdown
**Last Updated:** YYYY-MM-DD | **Verified against commit:** <short-hash>
```

Recent documentation updates (PR #27):
- Added verification banners to all 57 markdown files
- Ensures documentation stays in sync with codebase
- Track last verification date and commit hash

## Important Notes for AI Assistants

### Working Directory
- **Always** work from `/home/user/Semantic_Voice_Transcriber/`
- This is the root directory, not `Super_semantic_whisper/` (old name)

### Key Files to Check Before Making Changes
1. **CLAUDE.md** (this file): Overall guidance and architecture
2. **ARCHITECTURE.md**: Detailed technical architecture
3. **VERSION_STATUS.md**: Feature implementation status
4. **README.md**: User-facing documentation

### Testing Strategy
- Run relevant tests before committing: `python3 test_*.py`
- Use pytest for structured tests: `python3 -m pytest tests/`
- CI/CD tests available for fast validation (no real audio/API calls)
- Always test prosody extraction when modifying audio processing

### Code Conventions
- Use type hints where appropriate
- Document complex algorithms inline
- Follow existing patterns for consistency
- Preserve backward compatibility with V3 and V4 transcribers
- Add audit checks for new features in `audit/checks/`

### Configuration Management
- Never hardcode API keys or tokens
- Use environment variables or `.env` files
- Respect `config/psychoanalysis_config.yaml` settings
- Provider settings stored in `svt_core/config/settings.py`

### LLM Provider Integration
- Always support both OpenAI and Ollama paths
- Include health checks for new providers
- Handle rate limits and network errors gracefully
- Cache responses when appropriate (see `psychoanalysis_cache.py`)

### Prosody Analysis Best Practices
- Big 4 features are critical: Tempo, Pitch, Energy, Pauses
- Baseline calculation must precede deviation detection
- Align prosody segments with Whisper transcription segments (3-10s)
- Use Parselmouth for pitch (more accurate than librosa for speech)
- Store prosody data in JSON sidecar for LLM consumption

### Marker System
- ATO markers: Atomic patterns (18 root-level files)
- SEM markers: Semantic combinations (3 root-level files)
- VP_ATO: Voice-specific markers (16 files)
- Follow LeanDeep 3.5 schema: `id`, `frame`, `examples` (min 5)
- Test YAML syntax: `python3 test_yaml_structure.py`

### Documentation Updates
- Always update verification banner with current date and commit
- Keep CLAUDE.md synchronized with major changes
- Update VERSION_STATUS.md when completing features
- Cross-reference related documentation files
