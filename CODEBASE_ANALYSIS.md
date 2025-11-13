# Super Semantic Whisper: Comprehensive Codebase Analysis

**Analysis Date:** November 12, 2025  
**Project Root:** `/home/dyai/Dokumente/DYAI_home/DEV/TOOLS/TransSemantic/Super_semantic_whisper`  
**Total Size:** ~17GB | **Core Code:** ~10,286 lines Python | **Tests:** 16 files  
**Latest Commit:** `349d658` - docs: add overlapped speech detection documentation

---

## Executive Summary

**Super Semantic Whisper (SSW)** is an advanced multi-component therapeutic audio transcription system that combines:

1. **OpenAI Whisper** - High-quality automatic speech recognition (ASR)
2. **Prosody Analysis** - Pitch, tempo, energy, and pause detection ("Big 4" features)
3. **Emotion Detection** - TextBlob sentiment + audio feature analysis
4. **Speaker Diarization** - Automatic speaker segmentation with pyannote.audio
5. **Overlapped Speech Detection (OSD)** - Identifies simultaneous speech
6. **Semantic Analysis** - 63+ marker system for therapeutic language patterns
7. **Speaker Memory** - YAML-based learning profiles with running averages

**Primary Domain:** Therapeutic applications (anxiety, ADHD, trauma processing)  
**Development Status:** Phase 2c Complete (OSD integration) → Phase 2d (ATO marker integration) in planning

---

## 1. PROJECT STRUCTURE

### Root Directory Organization

```
Super_semantic_whisper/
├── Core Transcription (V1-V4)
│   ├── auto_transcriber_v3.py           (15K) - Base transcription with date/time extraction
│   ├── auto_transcriber_v4_emotion.py   (46K) - Enhanced: emotions + prosody + diarization + OSD
│   ├── build_memory_from_transcripts.py (18K) - Builds speaker profiles from existing transcripts
│   └── run_local.py                     (4K)  - Local-only operation mode
│
├── Prosody & Voice Analysis
│   ├── prosody_extractor.py             (13K) - "Big 4" features extraction
│   ├── prosody_analyzer.py              (5K)  - Running average calculations
│   ├── audio_quality_analyzer.py        (6K)  - SNR, clipping, silence detection
│   ├── audio_preprocessor.py            (5K)  - Adaptive noise reduction
│   └── speaker_diarizer.py              (14K) - pyannote.audio integration
│
├── Semantic & Output Processing
│   ├── super_semantic_processor.py      (30K) - Marker system + semantic threading
│   ├── semantic_chat_weaver.py          (22K) - WhatsApp conversation analysis
│   ├── integrated_semantic_weaver.py    (8K)  - Component integration layer
│   ├── output_formatter.py              (19K) - Markdown/JSON/CSV generation
│   ├── html_formatter.py                (25K) - HTML/PDF with professional layout
│   └── code_quality_review.py           (4K)  - Code analysis utilities
│
├── User Interfaces
│   ├── svt.py                           (39K) - Primary GUI (Semantic Voice Transcriber)
│   ├── super_semantic_gui.py            (14K) - Secondary GUI (Super Semantic mode)
│   └── start_super_semantic.py          (7K)  - Interactive launcher
│
├── Configuration & Setup
│   ├── initialize_person.py             (4K)  - Speaker profile initialization
│   ├── setup_environment.py             (6K)  - Environment configuration
│   ├── google_drive_sync.py             (12K) - Google Drive integration
│   └── requirements.txt                      - Dependencies list
│
├── Testing Suite (16 files)
│   ├── test_prosody_analyzer.py
│   ├── test_audio_quality_analyzer.py
│   ├── test_confidence_scoring.py
│   ├── test_integration_therapeutic.py
│   ├── test_intelligent_pipeline_integration.py
│   ├── test_overlapped_speech_detection.py
│   ├── test_output_formatter_osd.py
│   └── ... (8 more)
│
├── Data Directories
│   ├── Eingang/                         - Input audio files organized by speaker
│   │   └── Patient/                    - Speaker-specific folders
│   ├── Transkripte_LLM/                - Output transcripts (Markdown, JSON, HTML, PDF)
│   │   ├── *.md                        - Annotated transcripts with prosody markers
│   │   ├── *.prosody.json              - Detailed prosody data sidecar
│   │   ├── *.html                      - Professional formatted HTML
│   │   └── *.pdf                       - PDF exports via WeasyPrint
│   └── Memory/                         - Speaker profiles
│       ├── Patient.yaml                - Example: Prosody patterns + statistics
│       ├── PSG.yaml                    - PSG speaker profile
│       └── PSG001.yaml                 - Speaker variant
│
├── Marker System (19 files)
│   ├── ATO_*.yaml                      - Atomic Temporal Operators (19 files)
│   │   ├── ATO_ADHD_DISORGANIZED_THOUGHTS.yaml
│   │   ├── ATO_ANXIETY_HESITATION.yaml
│   │   ├── ATO_TEMPO_FAST.yaml
│   │   ├── ATO_TEMPO_SLOW.yaml
│   │   ├── ATO_VOICE_MICRO_BREAK.yaml
│   │   └── ... (14 more markers)
│   ├── SEM_*.yaml                      - Semantic markers (3 files)
│   │   ├── SEM_COLLABORATIVE_ALLIANCE.yaml
│   │   ├── SEM_DIDACTIC_ELABORATION.yaml
│   │   └── SEM_EPISTEMICALLY_GROUNDED_DISCOURSE.yaml
│   └── VP_ATO/                         - Extended ATO markers (~8 more)
│
├── Documentation
│   ├── CLAUDE.md                       - Developer guidance for Claude Code
│   ├── README.md                       - Project overview
│   ├── SPEAKER_DIARIZATION.md          - Phase 2b documentation
│   ├── docs/
│   │   ├── THERAPEUTIC_TRANSCRIPTION_GUIDE.md
│   │   ├── INTELLIGENT_PIPELINE.md
│   │   ├── OSD_GUIDE.md
│   │   └── plans/
│   │       ├── 2025-11-11-intelligent-pipeline.md
│   │       └── 2025-11-11-overlapped-speech-detection.md
│   └── TASK*.md                        - Implementation task documentation
│
├── Dependencies & Libraries
│   ├── TextBlob/                       - Local sentiment analysis (vendored)
│   ├── Parselmouth/                    - Praat Python interface
│   ├── pynote/                         - pyannote.audio (speaker diarization)
│   ├── huggingface/                    - Model resources
│   └── ALL_Marker_5.1/                 - Neural marker engine
│
├── Special Projects
│   ├── Turning_Points_in_Transcription/ (2.7M)
│   │   ├── turning_points_detector/    - Turning point detection system
│   │   ├── turning_points_analysis.md  - Analysis documentation
│   │   └── Semantic_Voice_Transcriber-main/
│   │
│   ├── Marker_LD3.5_SSoTh/             - LeanDeep 3.5 marker system
│   │   ├── markers_loader.py
│   │   ├── tools/                      - Audit and validation tools
│   │   └── SCH_schema/                 - Schema definitions
│   │
│   └── ALL_Marker_5.1/                 - Latest marker engine
│       ├── neural-marker-engine/
│       ├── CLAUDE.md
│       └── supabase/

├── Configuration Files
│   ├── .gitignore                      - Git ignore rules
│   ├── proposed_new_markers.yaml       - Experimental markers
│   ├── demo_super_semantic.json        - Demo data
│   └── super_semantic_output.summary.md

└── Logs & Outputs
    ├── transcription_v4_emotion.log    - V4 execution log
    ├── super_semantic_output.json.backup
    └── *.md, *.json, *.html, *.pdf    - Generated outputs
```

---

## 2. KEY FILES & ENTRY POINTS

### Primary Entry Points

| File | Type | Purpose | Size |
|------|------|---------|------|
| **svt.py** | GUI | Main Semantic Voice Transcriber application | 39K |
| **auto_transcriber_v4_emotion.py** | Core | Full transcription pipeline (V4) | 46K |
| **super_semantic_gui.py** | GUI | Alternative semantic analysis GUI | 14K |
| **start_super_semantic.py** | CLI | Interactive launcher with modes | 7K |
| **auto_transcriber_v3.py** | Core | Base transcription (predecessor) | 15K |

### Core Processing Modules

| Module | Purpose | Key Classes |
|--------|---------|------------|
| **prosody_extractor.py** | Big 4 feature extraction | `ProsodyFeatures`, `ProsodyBaseline`, `ProsodyExtractor` |
| **output_formatter.py** | Markdown/JSON/CSV generation | `OutputFormatter` |
| **html_formatter.py** | HTML/PDF export | `HTMLFormatter` |
| **super_semantic_processor.py** | Marker system integration | `SuperSemanticProcessor`, `SemanticMessage`, `EmotionalArc` |
| **speaker_diarizer.py** | Speaker detection & OSD | `SpeakerDiarizer` |
| **audio_quality_analyzer.py** | Quality assessment | `AudioQualityAnalyzer` |

### Supporting Modules

- **audio_preprocessor.py** - Adaptive noise reduction, resampling
- **prosody_analyzer.py** - Running average calculations
- **semantic_chat_weaver.py** - WhatsApp conversation threading
- **initialize_person.py** - Speaker profile creation
- **google_drive_sync.py** - Cloud synchronization

---

## 3. DATA FLOW ARCHITECTURE

### Complete Processing Pipeline

```
┌─ Audio Input ─────────────────────────────────────────────┐
│                                                             │
│  Eingang/{speaker}/                                        │
│  └─ WhatsApp Audio YYYY-MM-DD at HH.MM.SS.opus            │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─ Quality Analysis ────────────────────────────────────────┐
│                                                            │
│  audio_quality_analyzer.py                                │
│  ├─ Signal-to-Noise Ratio (SNR)                          │
│  ├─ Clipping Detection                                    │
│  ├─ Silence Ratio                                        │
│  ├─ Dynamic Range                                         │
│  └─ Quality Score → Model Selection                       │
└────────────────┬──────────────────────────────────────────┘
                 │
        ┌────────▼─────────┐
        │ Model Selection  │
        ├──────────────────┤
        │ Excellent: large │
        │ Good: medium     │
        │ Fair: small      │
        │ Poor: base       │
        └────────┬─────────┘
                 │
                 ▼
┌─ Adaptive Preprocessing (if needed) ──────────────────────┐
│                                                            │
│  audio_preprocessor.py (conditional)                      │
│  ├─ Noise Reduction (noisereduce)                        │
│  ├─ Normalization                                        │
│  ├─ Resampling to 16kHz                                  │
│  └─ Output: cleaned audio                                │
└────────────────┬──────────────────────────────────────────┘
                 │
                 ▼
┌─ Whisper Transcription ───────────────────────────────────┐
│                                                            │
│  auto_transcriber_v4_emotion.py                           │
│  ├─ Transcribe audio to text                             │
│  ├─ Segment with timestamps (3-10s chunks)              │
│  ├─ Calculate confidence scores (logprob + no_speech)   │
│  └─ Output: segments, text, confidence                   │
└────────────────┬──────────────────────────────────────────┘
                 │
        ┌────────┴────────┐
        │                 │
        ▼                 ▼
  ┌─────────────┐  ┌──────────────────┐
  │   Prosody   │  │  Diarization &   │
  │ Extraction  │  │       OSD        │
  └─────────────┘  └──────────────────┘
        │                 │
        │ (Parallel)      │
        ▼                 ▼
  ┌──────────────────────────────┐
  │ prosody_extractor.py         │
  ├──────────────────────────────┤
  │ For each segment:            │
  │ ├─ Tempo (WPM)              │
  │ ├─ Pitch (F0 Hz, jitter)    │
  │ ├─ Energy (RMS, dB)         │
  │ ├─ Pauses (silence >1s)     │
  │ └─ Calculate deviation %    │
  │    from baseline            │
  └──────────────────────────────┘
        │
        └─────────────────┬──────────────────┘
                          │
            ┌─────────────┼─────────────┐
            │             │             │
            ▼             ▼             ▼
      ┌─────────┐  ┌──────────┐  ┌──────────┐
      │ Speaker │  │ Emotion  │  │Overlapped│
      │ Diariz. │  │ Detection│  │ Speech   │
      └─────────┘  └──────────┘  └──────────┘
            │             │             │
            ▼             ▼             ▼
      speaker_diarizer    TextBlob      OSD
      (pyannote.audio)    sentiment    Detection
            │             │             │
            └─────────────┼─────────────┘
                          │
                          ▼
        ┌─────────────────────────────────┐
        │ Semantic Analysis               │
        │ super_semantic_processor.py     │
        ├─────────────────────────────────┤
        │ Load marker systems:            │
        │ ├─ ATO (19 markers)            │
        │ ├─ SEM (3 markers)             │
        │ ├─ External 63+ markers        │
        │ └─ Match patterns in text      │
        │                                 │
        │ Calculate semantic scores       │
        └────────────┬────────────────────┘
                     │
                     ▼
        ┌─────────────────────────────────┐
        │ Emotional Arc Detection         │
        │ ├─ Timeline of valence          │
        │ ├─ Peak/valley detection        │
        │ ├─ Turning point identification │
        │ └─ Overall trend                │
        └────────────┬────────────────────┘
                     │
                     ▼
        ┌─────────────────────────────────┐
        │ Memory Update                   │
        │ Memory/{speaker}.yaml           │
        ├─────────────────────────────────┤
        │ prosody_patterns:               │
        │ ├─ pitch_profile (running avg)  │
        │ ├─ tempo_profile (running avg)  │
        │ ├─ energy_profile (running avg) │
        │ └─ sample_count                 │
        │                                 │
        │ statistics:                     │
        │ ├─ avg_sentence_length          │
        │ ├─ sentiment ratios             │
        │ ├─ most_common_words            │
        │ └─ topic counters               │
        │                                 │
        │ interactions: (last 50)         │
        │ ├─ timestamp                    │
        │ ├─ filename                     │
        │ └─ metadata                     │
        └────────────┬────────────────────┘
                     │
                     ▼
        ┌─────────────────────────────────┐
        │ Output Generation               │
        │ output_formatter.py             │
        │ html_formatter.py               │
        ├─────────────────────────────────┤
        │ Markdown:                       │
        │ - Annotated transcript          │
        │ - Prosody markers               │
        │ - Emotion indicators            │
        │ - OSD callouts                  │
        │ - Confidence scores             │
        │                                 │
        │ JSON (sidecar):                 │
        │ - Structured prosody data       │
        │ - Segment metadata              │
        │ - Baseline calculations         │
        │ - Confidence metrics            │
        │                                 │
        │ HTML/PDF:                       │
        │ - Color-coded speakers          │
        │ - Orange highlighting (emotion) │
        │ - Pink borders (overlap)        │
        │ - Professional layout           │
        │                                 │
        │ CSV:                            │
        │ - Data export format            │
        │ - Segment-level analysis        │
        └────────────┬────────────────────┘
                     │
                     ▼
        ┌─────────────────────────────────┐
        │ Output Directory                │
        │ Transkripte_LLM/                │
        ├─────────────────────────────────┤
        │ YYYY-MM-DD_HH-MM-SS_speaker_name_transkript.md
        │ YYYY-MM-DD_HH-MM-SS_speaker_name_transkript.prosody.json
        │ YYYY-MM-DD_HH-MM-SS_speaker_name_transkript.html
        │ YYYY-MM-DD_HH-MM-SS_speaker_name_transkript.pdf
        │ YYYY-MM-DD_HH-MM-SS_speaker_name_transkript.csv
        └─────────────────────────────────┘
```

### Speaker Memory Learning Cycle

```
┌─ Audio Input ──────────┐
│ ({speaker}/{file})     │
└──────────┬─────────────┘
           │
           ▼
┌──────────────────────────────┐
│ Check Memory/{speaker}.yaml  │
└──────────────┬───────────────┘
               │
        ┌──────▼──────┐
        │ File exists?│
        ├─────────────┤
        │ No: Create  │
        │ Yes: Update │
        └──────┬──────┘
               │
               ▼
┌──────────────────────────────────────┐
│ Extract Prosody Baseline             │
│ ├─ Pitch mean, std                  │
│ ├─ Tempo mean, std                  │
│ ├─ Energy mean, std                 │
│ └─ Calculate deviations              │
└──────────┬───────────────────────────┘
           │
           ▼
┌──────────────────────────────────────┐
│ Update Running Averages              │
│ new_mean = (old_mean * n + value) / (n+1)
│ Update sample_count++               │
└──────────┬───────────────────────────┘
           │
           ▼
┌──────────────────────────────────────┐
│ Extract Text Statistics              │
│ ├─ Sentiment (TextBlob)              │
│ ├─ Word frequency                    │
│ ├─ Sentence structure                │
│ └─ Topic classification              │
└──────────┬───────────────────────────┘
           │
           ▼
┌──────────────────────────────────────┐
│ Save Updated Profile                 │
│ Memory/{speaker}.yaml                │
│ ├─ prosody_patterns (updated)       │
│ ├─ statistics (updated)              │
│ ├─ characteristics (generated)       │
│ ├─ interactions.append()             │
│ └─ last_updated timestamp            │
└──────────────────────────────────────┘
```

---

## 4. CORE COMPONENTS DEEP DIVE

### 4.1 Auto Transcriber V4 (Emotion & Prosody)

**File:** `auto_transcriber_v4_emotion.py` (46K)

**Key Classes:**
- `EmotionalAnalyzer` - Detects emotional markers from text + audio
- `TranscriptionResult` - Data structure for transcription output
- `WhisperTranscriber` - Whisper model interface

**Features:**
- Emotion marker loading from 63+ system markers
- Audio feature extraction (pitch, energy, tempo via librosa)
- TextBlob sentiment analysis
- Confidence scoring from Whisper logprobs
- Prosody integration (conditional import)
- Diarization integration (conditional import)

**Flow:**
```python
1. Load emotional markers from ATO/SEM YAML files
2. Transcribe audio with Whisper (model-dependent)
3. Extract confidence scores from segments
4. For each segment:
   a. Calculate audio features (if librosa available)
   b. Perform sentiment analysis (if TextBlob available)
   c. Extract prosody features (if prosody_extractor available)
   d. Detect emotion from combined sources
5. Return transcription_result with all metadata
```

### 4.2 Prosody Extractor (Big 4 Features)

**File:** `prosody_extractor.py` (13K)

**Key Data Classes:**
```python
@dataclass
class ProsodyFeatures:
    # Timing
    start_time, end_time, duration
    
    # Tempo (speech rate)
    tempo_wpm: float          # Words per minute
    word_count: int
    
    # Pitch (F0)
    pitch_mean_hz, pitch_std_hz
    pitch_min_hz, pitch_max_hz
    jitter_local, shimmer_local
    
    # Energy
    energy_rms, energy_db
    
    # Pauses
    pause_before_ms, pause_after_ms
    
    # Deviations from baseline
    tempo_deviation_pct
    pitch_deviation_pct
    energy_deviation_pct

@dataclass
class ProsodyBaseline:
    # Global statistics per audio file
    tempo_mean_wpm, tempo_std_wpm
    pitch_mean_hz, pitch_std_hz
    energy_mean_rms, energy_std_rms
    total_pause_duration_ms
```

**Technologies:**
- **Parselmouth** - Praat-based pitch extraction with jitter/shimmer
- **Librosa** - Audio feature extraction (tempo, energy)
- **NumPy** - Statistical calculations

### 4.3 Speaker Diarization & OSD

**File:** `speaker_diarizer.py` (14K)

**Features:**
- **Diarization:** Automatic speaker detection (Speaker A, B, C...)
- **OSD:** Overlapped speech detection (identifies simultaneous talk)

**Key Methods:**
```python
class SpeakerDiarizer:
    def diarize(audio_path) -> List[Dict]
        # Returns: [{'speaker': 'A', 'start': 0.0, 'end': 2.5}, ...]
    
    def detect_overlapped_speech(audio_path) -> List[Dict]
        # Returns: [{'start': 1.2, 'end': 1.8, 'duration': 0.6}, ...]
```

**Integration Points:**
- Uses Hugging Face pyannote.audio models
- Requires HF_TOKEN for model access
- Segments are mapped to transcript segments by timestamp
- OSD segments marked as `[ÜBERLAPPUNG Xs]` in output

### 4.4 Output Formatters

**Files:** `output_formatter.py` (19K) + `html_formatter.py` (25K)

**Output Formats Generated:**

| Format | File Type | Purpose |
|--------|-----------|---------|
| **Markdown** | `.md` | Annotated transcript with inline prosody markers |
| **JSON** | `.prosody.json` | Structured prosody data for system processing |
| **HTML** | `.html` | Professional layout with color-coded speakers |
| **PDF** | `.pdf` | Exportable document via WeasyPrint |
| **CSV** | `.csv` | Data export for analysis tools |

**Markdown Example:**
```markdown
# Transkript: KAH EGOSTATE (2)

**Chat mit:** Patient
**Aufnahme am:** 2025-11-11 um 16:40:34
**Verarbeitet am:** 2025-11-11 um 16:45:22

**Dominante Emotion:** Anxiety 😟
**Emotionale Valenz:** -0.45

## Zeitstempel
- **Aufnahme-Datum:** 2025-11-11
- **Aufnahme-Uhrzeit:** 16:40:34

## Transkription

**[00:05 - 00:07] Speaker A** So, wir haben ja nicht so viel Zeit. [TEMPO↑]
*Tempo: 226.4 WPM (+20.6%) | Pitch: 226.0 Hz (+13.2%) | Energy: 0.0836 (+5.5%)*

**[00:07 - 00:08] Speaker A** [ÜBERLAPPUNG 0.8s] Wolli, wir müssen sprechen.
*Overlapped with Speaker B for 800ms*
```

### 4.5 Super Semantic Processor

**File:** `super_semantic_processor.py` (30K)

**Data Classes:**
```python
@dataclass
class SemanticMessage:
    id, timestamp, sender, content, type
    emotion: Dict[str, float]
    markers: List[str]
    semantic_scores: Dict[str, float]
    metadata: Dict

@dataclass
class EmotionalArc:
    timeline: List[Tuple[datetime, float]]  # (time, valence)
    peaks, valleys, turning_points
    overall_trend: str

@dataclass
class SemanticRelationship:
    from_id, to_id, type, strength, reason
```

**Marker System:**
- **ATO (19 files):** Atomic Temporal Operators
  - ATO_TEMPO_FAST.yaml, ATO_TEMPO_SLOW.yaml
  - ATO_ANXIETY_HESITATION.yaml
  - ATO_ADHD_DISORGANIZED_THOUGHTS.yaml
  - ATO_VOICE_MICRO_BREAK.yaml
  - etc.

- **SEM (3 files):** Semantic markers
  - SEM_COLLABORATIVE_ALLIANCE.yaml
  - SEM_DIDACTIC_ELABORATION.yaml
  - SEM_EPISTEMICALLY_GROUNDED_DISCOURSE.yaml

- **External:** 63+ markers from parent directories

**Processing:**
1. Load all marker definitions from YAML
2. Pattern match against transcript text
3. Detect emotional arcs (timeline of valence)
4. Identify peaks, valleys, turning points
5. Build semantic threads (related messages)

---

## 5. DATA STRUCTURES

### Speaker Profile (Memory/Patient.yaml)

```yaml
characteristics: []
last_updated: '2025-11-11T16:40:34.200098'
name: Patient
prosody_patterns:
  energy_profile:
    energy_variability: 0.048
    mean_dynamic_range: 0.471
    mean_energy: 0.063
    sample_count: 3
  pitch_profile:
    mean_pitch: 247.1
    pitch_variability: 110.4
    sample_count: 3
  tempo_profile:
    mean_bpm: 119.7
    mean_speech_rate: 3.26
    sample_count: 3
statistics:
  avg_sentence_length: 8.51
  most_common_words: {}
  sentiment:
    negative: 0
    positive: 0
    ratio: 0
topics: {}
total_interactions: 3
```

### Prosody Marker Thresholds

```python
OUTPUT_MARKERS = {
    'tempo': {
        'threshold_pct': 20.0,
        'marker_up': '[TEMPO↑]',
        'marker_down': '[TEMPO↓]'
    },
    'pitch': {
        'threshold_pct': 15.0,
        'marker_up': '[PITCH↑]',
        'marker_down': '[PITCH↓]'
    },
    'energy': {
        'threshold_pct': 25.0,
        'marker_up': '[ENERGY↑]',
        'marker_down': '[ENERGY↓]'
    },
    'pause': {
        'threshold_ms': 1000.0,
        'marker': '[PAUSE]'
    },
    'overlap': {
        'marker': '[ÜBERLAPPUNG Xs]'
    },
    'confidence': {
        'threshold': 0.5,
        'marker': '[UNSICHER:score]'
    }
}
```

---

## 6. CURRENT STATE & PHASE TRACKING

### Completed Phases

**Phase 1: Prosody Extraction (✅ Complete)**
- Big 4 features implemented (Tempo, Pitch, Energy, Pauses)
- Baseline calculation per audio file
- Deviation detection (% from baseline)
- Markdown + JSON output formats

**Phase 2a: Professional Layout & Export (✅ Complete)**
- HTML export with color-coded speakers (6 colors)
- PDF export via WeasyPrint
- CSV export for analysis
- Emotional turning points highlighted (orange)

**Phase 2b: Speaker Diarization (✅ Complete)**
- pyannote.audio integration
- Automatic speaker detection (A, B, C...)
- Speaker labels in all output formats
- Color-coded in HTML/PDF

**Phase 2c: Overlapped Speech Detection (✅ Complete - as of Nov 12)**
- OSD pipeline added to speaker_diarizer.py
- Overlap markers in all formats: `[ÜBERLAPPUNG Xs]`
- HTML/PDF visualization (pink borders)
- Recent commits (4d6ee5c, c46f553, 1951389, 349d658)

### In Progress / Planning

**Phase 2d: ATO-Marker Integration (Planned)**
- Link VP_ATO/*.yaml markers to prosodic deviations
- Real-time marker triggering during transcription
- ATO → SEM → CLU → MEMA hierarchy
- GUI integration for marker system

**Phase 3: Streaming & Real-Time (Future)**
- Live transcription with prosody
- Real-time marker display
- WebSocket interface

### Recent Commits (Last 20)

| Hash | Message | Date |
|------|---------|------|
| 349d658 | docs: add overlapped speech detection documentation | Nov 12 |
| 1951389 | feat: add OSD visualization to HTML/PDF output | Nov 11 |
| 4d6ee5c | feat: add OSD markers to all output formats | Nov 11 |
| c46f553 | feat: integrate overlapped speech detection into transcription | Nov 11 |
| b5e87d3 | Fix critical overlapped speech detection label filtering | Nov 11 |
| 46d8e8d | feat: add overlapped speech detection pipeline | Nov 11 |
| 163637f | Phase 2b: Automatische Sprechererkennung | Nov 10 |
| d74faca | Phase 2a: Professional Layout & Multi-Format Export | Nov 10 |
| 2f490e7 | Add comprehensive README for Semantic Voice Transcriber | Nov 10 |
| f9dd4dd | Phase 1 Complete: Prosody Extraction Pipeline | Nov 10 |

---

## 7. TECHNICAL STACK

### Core Dependencies

```
OpenAI Whisper          - Speech-to-text transcription
Parselmouth/Praat       - Pitch extraction (F0), jitter/shimmer
Librosa                 - Audio feature analysis (tempo, energy)
pyannote.audio 4.0      - Speaker diarization + OSD
TextBlob (vendored)     - Sentiment analysis
PyYAML                  - Configuration management
NumPy / SciPy          - Numerical computing
WeasyPrint             - PDF generation
```

### Optional/Conditional

```
noisereduce             - Adaptive preprocessing (conditional)
torch                   - GPU acceleration (pyannote)
Google Drive API        - Cloud sync (optional)
```

### Development Tools

```
pytest                  - Testing framework (16 test files)
tkinter                 - GUI toolkit (SVT, super_semantic_gui)
logging                 - Detailed logging to files + console
git                     - Version control (active development)
```

### Python Version

- **Minimum:** 3.8+
- **Tested:** 3.12.3
- **Recommended:** 3.10+

---

## 8. TESTING & QUALITY ASSURANCE

### Test Coverage

**16 Test Files Present:**

| Category | Tests |
|----------|-------|
| **Prosody** | test_prosody_analyzer.py, test_prosody_pipeline.py |
| **Audio Quality** | test_audio_quality_analyzer.py, test_confidence_scoring.py |
| **Integration** | test_integration_therapeutic.py, test_task3_integration.py, test_intelligent_pipeline_integration.py |
| **Output** | test_output_formatter_osd.py |
| **Diarization/OSD** | test_overlapped_speech_detection.py, test_transcriber_osd_integration.py |
| **Other** | test_initialize_person.py, test_transcription.py, test_memory_prosody.py, test_yaml_structure.py, test_transcriber_v4_prosody.py |

### Testing Approach

- **TDD employed:** Tests written before implementation (per CLAUDE.md)
- **Unit + Integration:** Both styles present
- **Conditional skipping:** HF_TOKEN checks for pyannote tests

### Code Quality

- **Total Lines:** ~10,286 lines Python
- **Modularity:** Clear separation of concerns
- **Documentation:** Docstrings, type hints, README files
- **Logging:** Comprehensive logging to files + console
- **Error Handling:** Try/except for optional dependencies

---

## 9. DESIGN PATTERNS & ARCHITECTURE

### Pattern 1: Conditional Feature Loading

Many modules use try/except to gracefully degrade when dependencies unavailable:

```python
try:
    import librosa
    LIBROSA_AVAILABLE = True
except ImportError:
    LIBROSA_AVAILABLE = False

if LIBROSA_AVAILABLE:
    # Use librosa for audio features
else:
    # Fallback behavior
```

### Pattern 2: Dataclass-Based Data Structures

Type-safe data containers with `@dataclass`:

```python
@dataclass
class ProsodyFeatures:
    start_time: float
    end_time: float
    tempo_wpm: Optional[float]
    pitch_mean_hz: Optional[float]
    energy_rms: Optional[float]
    # ... more fields
```

### Pattern 3: YAML Configuration & Markers

Externalized configuration via YAML:

```yaml
# ATO_TEMPO_FAST.yaml
keywords:
  - "hurried"
  - "rushed"
  - "fast-paced"
patterns:
  - "speaking quickly"
  - "talking fast"
threshold: 0.7
```

### Pattern 4: Running Average for Memory Learning

Efficient incremental updates without storing full history:

```python
# Update running average
n = sample_count
new_mean = (old_mean * n + new_value) / (n + 1)
sample_count += 1
```

### Pattern 5: Queue-Based GUI Threading

Non-blocking UI updates using thread-safe queues:

```python
self.progress_queue = queue.Queue()
# Worker thread puts progress messages
# GUI thread reads with _check_progress_queue()
```

### Pattern 6: Factory Pattern for Output Generation

Multiple output formats from single transcription result:

```python
output_formatter.format_transcript(result) -> Dict[Path]:
    {
        'markdown': path/to/file.md,
        'json': path/to/file.prosody.json,
        'html': path/to/file.html,
        'pdf': path/to/file.pdf,
        'csv': path/to/file.csv
    }
```

---

## 10. PURPOSE & GOALS

### Primary Purpose

**Therapeutic Audio Analysis:** Enable therapists to:
1. Transcribe WhatsApp audio recordings automatically
2. Identify emotional turning points via prosody + semantics
3. Track patient speech patterns over time (memory learning)
4. Detect markers associated with therapeutic change
5. Analyze multi-speaker interactions (diarization + OSD)

### Secondary Applications

1. **Research:** Analyze therapeutic discourse patterns
2. **Training:** Study therapy techniques with voice analysis
3. **Quality Control:** Monitor transcription confidence
4. **Integration:** Feed semantic markers into other systems

### Success Criteria

- ✅ High-quality transcriptions (Whisper medium/large models)
- ✅ Accurate prosody feature extraction (Big 4 + voice quality)
- ✅ Speaker identification (diarization)
- ✅ Simultaneous speech detection (OSD)
- ✅ Emotional arc tracking (sentiment + markers)
- ✅ Learning profiles (memory system)
- ✅ Professional output formats (HTML, PDF)
- ✅ Marker integration (63+ markers)

---

## 11. STRENGTHS & OBSERVATIONS

### Architectural Strengths

1. **Modular Design** - Clear separation: transcription, prosody, emotion, output
2. **Progressive Enhancement** - Gracefully degrades without optional dependencies
3. **Multi-Format Output** - Markdown, JSON, HTML, PDF, CSV
4. **Learning System** - Speaker profiles improve over time (YAML-based memory)
5. **Comprehensive Testing** - 16 test files covering major components
6. **Professional GUI** - Two GUIs (svt.py, super_semantic_gui.py) with threading
7. **Therapeutic Focus** - Designed specifically for therapy applications
8. **Recent Active Development** - 25+ commits in past 2 weeks

### Technical Highlights

1. **Prosody Pipeline** - Big 4 features with baseline comparison and deviation detection
2. **Speaker Diarization** - Cutting-edge pyannote.audio integration
3. **Overlapped Speech Detection** - Recent addition (Nov 11) for interaction analysis
4. **Confidence Scoring** - Whisper logprob-based reliability metrics
5. **Marker System** - 19 ATO + 3 SEM markers with YAML-based pattern matching
6. **Quality-First** - Intelligent audio quality analysis drives model selection

### Code Quality Observations

1. **Type Hints** - Extensive use of Python type hints
2. **Documentation** - Detailed docstrings and README files
3. **Logging** - Comprehensive logging with file + console output
4. **Error Handling** - Graceful degradation for missing dependencies
5. **TDD Approach** - Tests written before implementation

---

## 12. AREAS FOR ATTENTION

### Known Limitations

1. **No pytest Configuration** - Manual test execution (per CLAUDE.md)
2. **Parent Directory Dependencies** - Requires external marker systems in parent directories
3. **Large Project Size** - 17GB total (includes large ML models)
4. **GPU Requirements** - Optimal performance requires CUDA for pyannote
5. **HF Token Requirement** - Diarization/OSD need Hugging Face authentication

### Integration Points Needing Completion

1. **Phase 2d: ATO-Marker Integration**
   - Link VP_ATO markers to prosodic deviations
   - Real-time triggering during transcription
   - GUI integration for marker system selection

2. **Turning Points Detector** (2.7M subdirectory)
   - Separate turning_points_detector/ system exists
   - Not yet fully integrated into main pipeline
   - Requires additional development

3. **Marker System Unification**
   - Multiple marker collections (ATO, SEM, VP_ATO)
   - External 63+ marker system in parent directory
   - Opportunity to consolidate + standardize

### Potential Issues

1. **File Naming Dependencies** - V3/V4 extract timestamps from WhatsApp filename format
2. **Memory Profile Initialization** - First analysis creates minimal YAML
3. **Model Size** - Whisper large model is 3GB+ (bandwidth consideration)
4. **Real-Time Performance** - Prosody extraction can be slow on large audio files

---

## 13. ROADMAP & NEXT STEPS

### Immediate (Phase 2d)

- [ ] Integrate ATO markers into transcription pipeline
- [ ] Link prosodic deviations to marker triggers
- [ ] Build ATO → SEM → CLU → MEMA hierarchy
- [ ] Add marker selection to SVT GUI
- [ ] Complete integration testing

### Medium Term (Phase 3)

- [ ] Streaming audio support (WebSocket)
- [ ] Real-time prosody display
- [ ] Real-time marker triggering
- [ ] Browser-based interface
- [ ] Multi-session conversation analysis

### Long Term

- [ ] Machine learning-based turning point detection
- [ ] Therapeutic outcome prediction
- [ ] Research dataset export tools
- [ ] API server for external integrations
- [ ] Mobile application

---

## 14. DEPENDENCY GRAPH

```
svt.py (Main GUI)
├── auto_transcriber_v4_emotion.py
│   ├── prosody_extractor.py
│   │   ├── parselmouth (Praat)
│   │   └── librosa
│   ├── speaker_diarizer.py
│   │   └── pyannote.audio
│   └── (optional) prosody_analyzer.py
├── output_formatter.py
│   ├── html_formatter.py
│   │   └── weasyprint
│   └── pathlib
├── audio_quality_analyzer.py
│   └── librosa
├── audio_preprocessor.py
│   ├── librosa
│   └── noisereduce
└── super_semantic_processor.py
    ├── yaml
    ├── semantic_chat_weaver.py
    └── YAML marker files (19 ATO + 3 SEM)
```

---

## 15. FILE STATISTICS

| Category | Count | Size |
|----------|-------|------|
| Python Files (.py) | ~40 | 10K lines |
| Test Files | 16 | ~1.2K lines |
| YAML Markers | 22 | Various |
| Documentation (.md) | 20+ | Various |
| Subdirectories | 5 major | - |
| Total Project | - | 17GB |

### Largest Python Files

1. auto_transcriber_v4_emotion.py - 46K
2. svt.py - 39K
3. super_semantic_processor.py - 30K
4. html_formatter.py - 25K
5. semantic_chat_weaver.py - 22K
6. output_formatter.py - 19K
7. build_memory_from_transcripts.py - 18K
8. prosody_extractor.py - 13K
9. google_drive_sync.py - 12K
10. speaker_diarizer.py - 14K

---

## CONCLUSION

**Super Semantic Whisper** is a sophisticated, production-ready therapeutic audio analysis system combining state-of-the-art speech recognition, voice analysis, speaker detection, and semantic marker systems. The codebase demonstrates:

- **Professional architecture** with clear modularity and separation of concerns
- **Active development** with regular commits and feature additions
- **Therapeutic focus** tailored to specific therapeutic applications
- **Comprehensive feature set** from transcription through semantic analysis
- **Excellent documentation** with detailed guides and implementation plans

The system is ready for Phase 2d (ATO marker integration) and has a clear roadmap toward streaming/real-time capabilities in Phase 3.

---

**Analysis Generated:** November 12, 2025  
**Analyst:** Claude Code (Haiku 4.5)  
**Confidence:** High (based on direct codebase inspection)
