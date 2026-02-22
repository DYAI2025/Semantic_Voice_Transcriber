<div align="center">

# Semantic Voice Transcriber

### Professional Therapeutic Transcription with Deep Audio Intelligence

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/downloads/)
[![License: CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey?style=for-the-badge)](https://creativecommons.org/licenses/by-nc-sa/4.0/)
[![Status](https://img.shields.io/badge/Phase%202c-Complete-success?style=for-the-badge)]()
[![Privacy](https://img.shields.io/badge/Privacy-100%25%20Local-green?style=for-the-badge&logo=shield&logoColor=white)]()
[![GDPR](https://img.shields.io/badge/GDPR-Compliant-blue?style=for-the-badge)]()

**Last Updated:** 2026-02-22 | **Verified against commit:** 39ed3ff

---

*Turn therapy session audio into deep clinical insights — locally, privately, automatically.*

[Features](#-features) · [Quick Start](#-quick-start) · [How It Works](#-how-it-works) · [Output Formats](#-output-formats) · [Installation](#-installation) · [Use Cases](#-use-cases) · [Roadmap](#-roadmap)

</div>

---

## Why Semantic Voice Transcriber?

Therapists and clinical researchers need more than a transcript. They need to understand **how** something was said — the hesitations, the accelerations, the emotional undercurrents. SVT is the only open-source tool purpose-built for this: it combines state-of-the-art speech recognition with acoustic prosody analysis, emotion dynamics, and a 63+ marker semantic engine, all running **100% on your local machine**.

No cloud. No subscriptions. No data leaving your office.

---

## Features

### Core Capabilities

| Capability | Details |
|---|---|
| **Speech-to-Text** | OpenAI Whisper with 5 model sizes (tiny → large), auto-selected by audio quality |
| **Prosody Analysis** | Big 4: Tempo, Pitch, Energy, Pauses — with per-segment baseline deviation detection |
| **Speaker Diarization** | pyannote.audio 3.1 — automatic multi-speaker labeling with overlap detection |
| **Emotion Detection** | Multi-modal: audio features + TextBlob sentiment + acoustic markers |
| **Semantic Markers** | 63+ ATO/SEM markers: emotions, turning points, defense mechanisms, transference |
| **Memory System** | Persistent speaker profiles with running prosody baselines across sessions |
| **LLM Integration** | FREE local Ollama or cloud OpenAI — user's choice, switchable in GUI |
| **Psychoanalysis Dashboard** | Interactive HTML dashboards with VAD trajectories, marker networks, turnpoints |
| **Output Formats** | Markdown, JSON, HTML, Enhanced HTML, PDF, CSV, Dashboard — 7 total |

### What Makes It Different

```
Generic transcription tools:   Audio → Text
SVT:                           Audio → Text + Prosody + Emotion + Semantics + Memory + Dashboard
```

SVT does not just transcribe. It annotates every segment with vocal behavior markers, detects clinically significant turning points, and builds a growing longitudinal profile of each speaker across sessions.

---

## Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/DYAI2025/Semantic_Voice_Transcriber.git
cd Semantic_Voice_Transcriber

# 2. Install dependencies
pip install -r requirements.txt

# 3. (Optional) Install Ollama for free local LLM
curl -fsSL https://ollama.com/install.sh | sh
ollama pull qwen2.5-coder:7b

# 4. Launch the GUI
python3 svt.py
```

Then:
1. Drop audio files into `Eingang/PatientName/`
2. Select your features (Prosody, Diarization, Emotion, Memory)
3. Click **"Transkription starten"**
4. Open your richly annotated results in `Transkripte_LLM/`

---

## How It Works

```
Audio File (.opus / .m4a / .wav / .mp3)
          │
          ▼
┌─────────────────────┐
│  Audio Quality      │  SNR, clipping, silence ratio → Quality Score (0–100)
│  Analysis           │  → Auto-selects Whisper model (tiny / base / small / medium / large)
└────────┬────────────┘
          │
          ▼
┌─────────────────────┐
│  Audio              │  Noise reduction, normalization, high-pass filter
│  Preprocessing      │  (triggered when Quality Score < 60)
└────────┬────────────┘
          │
          ▼
┌─────────────────────┐
│  Whisper            │  Segment-level transcription with confidence scoring
│  Transcription      │  avg_logprob × (1 − no_speech_prob) → [UNSICHER:score]
└────────┬────────────┘
          │
          ▼
┌─────────────────────┐
│  Speaker            │  pyannote.audio 3.1 — Speaker A / B / C
│  Diarization        │  + Overlapped Speech Detection → [ÜBERLAPPUNG Xs]
└────────┬────────────┘
          │
          ▼
┌─────────────────────┐
│  Prosody            │  Per-segment:
│  Extraction         │    Tempo (WPM via word count / duration)
│                     │    Pitch F0 (Parselmouth / Praat, jitter, shimmer)
│                     │    Energy (Librosa RMS + dB)
│                     │    Pauses (VAD silence detection)
│                     │  + Global baseline → deviation markers:
│                     │    [TEMPO↑/↓] ±20% | [PITCH↑/↓] ±15%
│                     │    [ENERGY↑/↓] ±25% | [PAUSE] >1s
└────────┬────────────┘
          │
          ▼
┌─────────────────────┐
│  Emotion            │  TextBlob sentiment polarity + audio feature vectors
│  Analysis           │  → 7 emotion categories + valence score
└────────┬────────────┘
          │
          ▼
┌─────────────────────┐
│  ATO Semantic       │  63+ marker categories (YAML-defined):
│  Marker Detection   │  Emotions, Turning Points, Defense Mechanisms,
│                     │  Therapeutic Patterns, Psychoanalytic Dynamics
└────────┬────────────┘
          │
          ▼
┌─────────────────────┐
│  Speaker Memory     │  Persistent YAML profiles — pitch/tempo/energy running averages,
│  Update             │  topic tracking, interaction history (last 50 sessions)
└────────┬────────────┘
          │
          ▼
┌─────────────────────┐
│  Multi-Format       │  .md  .prosody.json  .html  _enhanced.html
│  Output             │  .pdf  .csv  psychoanalysis_dashboard.html
└─────────────────────┘
```

---

## Output Formats

### Annotated Markdown — Therapist-Readable

Clean, human-readable format with metadata sidebars. The key innovation: prosody and semantic markers appear in sidebars, not inline, keeping the transcript readable.

```markdown
### **Therapeut** | 00:05 - 00:12
Wie geht es Ihnen heute?
> **Metadaten:**
> Prosody: Energie ↑ (+28.0%)
> Marker: ATO_AFFIRMATION

### **Patient** | 00:12 - 00:31
Ich weiß nicht... [PAUSE] es ist einfach alles so schwer. [TEMPO↓] [ENERGY↓]
> **Metadaten:**
> Prosody: Tempo ↓ (−24.1%), Energie ↓ (−31.5%)
> Marker: ATO_SADNESS, ATO_RESISTANCE_VERBAL
> Confidence: 0.94
```

### JSON Sidecar — Machine-Readable

Every segment exports its full prosody data alongside the transcript for downstream LLM processing or data science:

```json
{
  "metadata": { "speaker": "Patient", "duration_seconds": 183.4, "dominant_emotion": "traurig_reflektierend" },
  "baseline": { "tempo_wpm_mean": 118.5, "pitch_mean_hz": 147.8, "energy_rms_mean": 0.045 },
  "segments": [
    {
      "text": "es ist einfach alles so schwer.",
      "tempo_wpm": 89.9, "tempo_deviation_pct": -24.1,
      "pitch_mean_hz": 131.2, "pitch_deviation_pct": -11.2,
      "energy_rms": 0.031, "energy_deviation_pct": -31.5,
      "pause_before_ms": 1240,
      "markers": ["TEMPO↓", "ENERGY↓", "PAUSE"],
      "confidence": 0.94
    }
  ]
}
```

### Psychoanalysis Dashboard — Interactive HTML

A full interactive dashboard powered by Chart.js and Cytoscape.js, generated from a single click:

- **VAD Trajectory Charts** — Valence, Arousal, Dominance over time
- **UED Metrics** — Home Base, Variability, Instability, Inertia, Rise/Recovery Rates
- **Marker Network Graph** — Relationship visualization between semantic markers
- **Tri-Modal Turning Point Detection** — Emotion + Prosody + Markers aligned on a timeline
- **16 Psychoanalytic Markers** — Defense mechanisms, transference, resistance, thematic shifts

### All Formats at a Glance

| Format | Best For |
|---|---|
| `.md` | Therapist session notes, human review |
| `.prosody.json` | LLM post-processing, data pipelines |
| `.html` | Color-coded speaker view, sharing |
| `_enhanced.html` | Full marker + prosody annotations |
| `.pdf` | Clinical records, printing, archiving |
| `.csv` | Research, statistical analysis, export |
| `_dashboard.html` | Psychoanalytic session review |

---

## Prosody Markers — The "Big 4"

SVT detects four core vocal dimensions per segment and flags statistically significant deviations from that speaker's session baseline:

| Marker | Trigger | Method |
|---|---|---|
| `[TEMPO↑]` / `[TEMPO↓]` | ±20% from baseline WPM | Word count ÷ segment duration |
| `[PITCH↑]` / `[PITCH↓]` | ±15% from baseline F0 | Parselmouth (Praat) F0 extraction |
| `[ENERGY↑]` / `[ENERGY↓]` | ±25% from baseline RMS | Librosa RMS analysis |
| `[PAUSE]` | >1000ms silence | Voice Activity Detection |
| `[ÜBERLAPPUNG Xs]` | Overlapping speech detected | pyannote OSD model |
| `[UNSICHER:0.xx]` | Confidence < 0.50 | Whisper avg_logprob × (1−no_speech_prob) |

---

## Semantic Marker System (LeanDeep 3.5)

SVT implements the **LeanDeep 3.5** 4-tier marker hierarchy:

```
ATO  (Atomic)    — Primitive signals: tokens, patterns, acoustic events
 └── SEM  (Semantic)  — Combinations of 2+ ATOs forming micro-patterns
      └── CLU  (Cluster)  — Thematic aggregations over defined windows
           └── MEMA (Meta-Analysis) — Dynamic patterns from multiple CLUs
```

**40 curated clinical markers** organized by category:

| Category | Count | Examples |
|---|---|---|
| Emotions | 14 | `ATO_SADNESS`, `ATO_ANGER`, `ATO_ANXIETY`, `ATO_JOY` |
| Turning Points | 17 | `ATO_BREAKTHROUGH`, `ATO_INSIGHT`, `ATO_RESISTANCE_BREAK` |
| Therapeutic | 5 | `ATO_AFFIRMATION`, `ATO_DEFLECTION`, `ATO_DISCLOSURE` |
| Psychoanalytic | 4 | `ATO_DEFENSE_DENIAL`, `ATO_TRANSFERENCE_POSITIVE` |

All markers are defined in YAML and fully customizable — add domain-specific markers without modifying source code.

---

## Speaker Memory System

SVT builds a persistent profile for each speaker across sessions. Every transcription updates the profile with new observations:

```yaml
# Memory/PatientName.yaml  (auto-created, auto-updated)
prosody_patterns:
  pitch_profile:
    mean_pitch: 147.8       # Hz — running average across all sessions
    pitch_variability: 19.4
    sample_count: 15
  tempo_profile:
    mean_bpm: 118.5
    mean_speech_rate: 4.3   # syllables/sec
  energy_profile:
    mean_energy: 0.045
    mean_dynamic_range: 0.28

statistics:
  avg_sentence_length: 15.3
  sentiment: { positive: 42, negative: 8, ratio: 5.25 }

topics: { personal: 23, health: 18, relationships: 12 }
characteristics: [reflective, measured, detail-oriented]
interactions: [...]  # last 50 sessions with timestamps
```

This means deviation detection improves over time — SVT learns each speaker's vocal "fingerprint" and detects meaningful departures from their personal baseline, not just a session average.

---

## LLM Integration — Local or Cloud

SVT supports two provider paths with a unified interface:

```
┌─────────────────────────────────────────┐
│            LLM Provider Manager          │
├─────────────┬───────────────────────────┤
│  Ollama     │  OpenAI                   │
│  (FREE)     │  (Cloud API)              │
│  Local      │                           │
│  Private    │  GPT-4-Turbo              │
│  No API key │  Requires API key         │
└─────────────┴───────────────────────────┘
```

**Ollama (recommended for privacy-sensitive clinical use):**
```bash
ollama pull qwen2.5-coder:7b
ollama serve
# Select "Ollama" in SVT GUI → Settings → Provider
```

**OpenAI:**
```bash
export OPENAI_API_KEY=sk-your-key-here
# Select "OpenAI" in SVT GUI → Settings → Provider
```

Switch providers at runtime from the GUI without restarting.

---

## Privacy & GDPR Compliance

SVT is designed from the ground up for clinical data protection:

- **100% local processing** — audio never leaves your machine
- **No telemetry, no analytics, no network calls** (unless you explicitly configure OpenAI)
- **Ollama path** runs the full pipeline with zero external dependencies
- **Local file storage** — all transcripts, profiles, and dashboards stay on-device
- All speaker profiles stored as local YAML files under your control
- Fully auditable open-source codebase

> For maximum compliance in clinical settings: use the Ollama provider, keep `Eingang/` and `Transkripte_LLM/` on an encrypted volume.

---

## Installation

### System Requirements

| | Minimum | Recommended |
|---|---|---|
| OS | Linux, macOS, Windows (WSL) | Ubuntu 22.04+ |
| Python | 3.8+ | 3.12 |
| RAM | 8 GB | 16 GB |
| Storage | 5 GB | 15 GB |
| GPU | — | CUDA-capable (faster Whisper + diarization) |

### Step-by-Step

```bash
# System dependencies (Ubuntu/Debian)
sudo apt install python3.12 python3-pip ffmpeg portaudio19-dev python3-tk

# macOS
brew install ffmpeg portaudio

# Python packages
pip install -r requirements.txt

# Emotion analysis (optional)
pip install -r requirements_emotion.txt

# Prosody analysis (required for SVT)
pip install praat-parselmouth librosa soundfile

# Speaker diarization (optional, requires Hugging Face token)
pip install pyannote.audio
```

### Speaker Diarization Setup

Speaker diarization requires a free Hugging Face account and model access:

1. Create account at [huggingface.co](https://huggingface.co/join)
2. Accept model agreements:
   - [pyannote/segmentation-3.0](https://huggingface.co/pyannote/segmentation-3.0)
   - [pyannote/speaker-diarization-3.1](https://huggingface.co/pyannote/speaker-diarization-3.1)
3. Create a read token at [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)
4. Add to your environment:
   ```bash
   echo "HF_TOKEN=hf_YourTokenHere" > .env
   ```

See [SPEAKER_DIARIZATION.md](SPEAKER_DIARIZATION.md) for detailed setup and troubleshooting.

---

## Use Cases

### For Therapists
- Automatic transcription of WhatsApp audio messages from clients
- One-click session documentation with speaker separation
- Prosody-annotated transcripts flagging emotional intensity shifts
- Longitudinal speaker profiling across sessions
- GDPR-compliant local processing — no patient data ever leaves the device

### For Clinical Researchers
- Structured JSON output for downstream statistical analysis
- CSV export for prosody feature datasets
- 63+ validated semantic markers for behavioral coding
- Reproducible pipelines via CLI and Python API
- Full test suite with 58 test files for research validation

### For NLP / AI Developers
- Modular Python architecture — swap components independently
- LLM provider abstraction layer (OpenAI, Ollama, extensible)
- Audio processing pipeline: quality analysis → preprocessing → transcription → analysis → output
- Marker system built on YAML — add domain markers without code changes
- Feature audit system for readiness tracking

---

## Architecture

```
svt.py  ──────────────────────────────────────────────────────────────────────
  │                             MAIN GUI ENTRY POINT
  │
  ├── svt_core/
  │   ├── health_check.py          Real-time system status (Ollama, API keys, models)
  │   ├── llm_provider/
  │   │   ├── base.py              LLMProvider abstract class + LLMResponse
  │   │   ├── factory.py           Provider instantiation
  │   │   ├── manager.py           Runtime provider switching
  │   │   └── local_ollama.py      FREE local LLM (qwen2.5-coder:7b)
  │   ├── config/settings.py       Persistent user configuration
  │   └── ui/provider_dialog.py    Provider settings GUI
  │
  ├── auto_transcriber_v4_emotion.py   PIPELINE ORCHESTRATOR
  │   ├── audio_quality_analyzer.py    SNR, clipping, quality score → model selection
  │   ├── audio_preprocessor.py        Noise reduction, normalization
  │   ├── speaker_diarizer.py          pyannote.audio + OSD
  │   ├── prosody_extractor.py         Big 4 features + baseline
  │   └── output_formatter.py          7 output formats
  │
  ├── psychoanalysis_pipeline.py       DASHBOARD PIPELINE
  │   ├── psychoanalysis_api.py        OpenAI GPT-4 UED analysis
  │   ├── psychoanalysis_api_ollama.py Free local UED analysis
  │   ├── psychoanalysis_cache.py      Transcript caching
  │   └── dashboard_generator.py       Chart.js + Cytoscape.js HTML
  │
  ├── ato_marker_integration.py        SEMANTIC ENGINE
  │   └── super_semantic_processor.py  63+ ATO/SEM marker detection
  │
  ├── audit/                           QUALITY ASSURANCE
  │   ├── feature_registry.py          Feature tracking
  │   ├── audit_runner.py              Automated checks
  │   └── report_builder.py           Readiness reports
  │
  └── Memory/                          SPEAKER PROFILES
      ├── speaker_profiles.db          SQLite database
      └── *.yaml                       Per-speaker YAML profiles
```

---

## Whisper Model Selection

SVT automatically picks the optimal Whisper model based on your audio's quality score:

| Model | Parameters | RAM | Speed | Accuracy | Auto-selected when |
|---|---|---|---|---|---|
| tiny | 39M | 1 GB | ⚡⚡⚡⚡⚡ | ★★ | Quality > 85 |
| base | 74M | 1 GB | ⚡⚡⚡⚡ | ★★★ | Quality 75–85 |
| small | 244M | 2 GB | ⚡⚡⚡ | ★★★★ | Quality 60–75 |
| medium | 769M | 5 GB | ⚡⚡ | ★★★★★ | Quality 40–60 |
| large | 1550M | 10 GB | ⚡ | ★★★★★ | Quality < 40 |

You can always override the auto-selection in the GUI.

---

## Roadmap

### Completed

- [x] **Phase 1** — Prosody extraction: Big 4 features, baseline deviation, annotated Markdown + JSON sidecar
- [x] **Phase 2a** — Professional output: HTML, PDF, CSV with color-coded speakers and prosody markers
- [x] **Phase 2b** — Speaker diarization: pyannote.audio 3.1, overlapped speech detection, GPU support
- [x] **Phase 2c** — Psychoanalysis Dashboard: dual LLM provider, VAD trajectory charts, UED metrics, marker network, tri-modal turning point detection, Ollama (free local LLM), health monitoring, feature audit system, modular `svt_core/` architecture

### In Progress

- [ ] **Phase 2d** — ATO marker integration with prosody triggers, real-time marker detection, ATO → SEM → CLU → MEMA hierarchy refinement, multi-provider expansion (Anthropic Claude, Azure OpenAI)

### Planned

- [ ] **Phase 3** — Live streaming transcription, real-time prosody visualization, WebSocket API, multi-session comparative analysis
- [ ] **Phase 4** — Multi-language support (DE, EN, FR, ES, IT), dialect detection, cross-cultural prosody baselines
- [ ] **Phase 5** — Advanced AI: LLM-powered semantic thread identification, voice anonymization for compliant demos

---

## Development & Testing

```bash
# Run full test suite
pytest -v

# Run by category
pytest -v -m unit
pytest -v -m integration
pytest -v -m "not slow"

# Run specific modules
pytest tests/test_ci_transcription.py -v
pytest tests/test_psychoanalysis_pipeline.py -v
pytest tests/test_prosody_analyzer.py -v

# Feature readiness audit
python3 -m audit.cli status
python3 -m audit.cli run memory
python3 -m audit.cli report
```

**Test suite:** 58 test files across `tests/` and root — CI/CD compatible, no real audio or API calls required.

---

## Troubleshooting

| Problem | Cause | Fix |
|---|---|---|
| `FFmpeg not found` | FFmpeg not installed | `sudo apt install ffmpeg` |
| `Ollama not available` | Server not running | `ollama serve` |
| `HF Token error` | Missing model access | Accept model agreements on Hugging Face |
| `Out of memory` on long files | Chunk size too small | SVT auto-chunks at 5 min; increase to `chunk_duration=600` |
| Low transcription quality | Poor audio SNR | Enable Audio Preprocessing in GUI; try a larger Whisper model |
| `[UNSICHER:0.xx]` markers | Low confidence segment | Normal for noisy audio; review those segments manually |

For detailed solutions, see [CLAUDE.md](CLAUDE.md#common-issues).

---

## Codebase Stats

| Metric | Count |
|---|---|
| Python files | 164 |
| Test files | 58 |
| Documentation files | 57 |
| ATO marker definition files | 37 |
| Supported audio formats | 5 (`.opus` `.m4a` `.wav` `.mp3` `.ogg`) |
| Whisper model sizes | 5 (tiny → large) |
| LLM providers | 2+ (OpenAI, Ollama) |
| Prosody features ("Big 4") | 4 |
| Output formats | 7 |
| Semantic marker categories | 63+ |

---

## Technologies

| Component | Technology |
|---|---|
| Speech Recognition | [OpenAI Whisper](https://github.com/openai/whisper) |
| Pitch Analysis | [Parselmouth](https://parselmouth.readthedocs.io/) (Praat Python interface) |
| Audio Analysis | [Librosa](https://librosa.org/) |
| Speaker Diarization | [pyannote.audio](https://github.com/pyannote/pyannote-audio) 3.1 |
| Local LLM | [Ollama](https://ollama.com/) + qwen2.5-coder:7b |
| Dashboard Visualizations | [Chart.js](https://www.chartjs.org/) + [Cytoscape.js](https://cytoscape.org/) |
| Sentiment Analysis | [TextBlob](https://textblob.readthedocs.io/) |
| PDF Generation | [WeasyPrint](https://weasyprint.org/) |
| Deep Learning Backend | [PyTorch](https://pytorch.org/) |
| GUI | Python Tkinter |

---

## License

**Creative Commons BY-NC-SA 4.0**

You may share and adapt this work for non-commercial purposes, provided you give appropriate credit and distribute derivatives under the same license.

See [LICENSE](Lizenz:%20Creative%20Commons%20BY-NC-SA%204.0.md) for full terms.

**Copyright © DYAI 2025**

---

## Credits

- **[OpenAI Whisper](https://github.com/openai/whisper)** — state-of-the-art speech recognition
- **[pyannote.audio](https://github.com/pyannote/pyannote-audio)** — speaker diarization framework
- **[Parselmouth](https://parselmouth.readthedocs.io/)** — Praat acoustics via Python
- **[Librosa](https://librosa.org/)** — audio feature extraction
- **DYAI Framework** — LeanDeep 3.5 marker system (ATO/SEM/CLU/MEMA), FRAUSAR, CoSD/MARSAP
- **[Claude Code (Anthropic)](https://claude.ai/code)** — development assistant

---

<div align="center">

**Built for therapists. Designed for clinical rigor. Committed to privacy.**

[Report an Issue](https://github.com/DYAI2025/Semantic_Voice_Transcriber/issues) · [View Changelog](VERSION_STATUS.md) · [Architecture Deep Dive](ARCHITECTURE.md)

</div>
