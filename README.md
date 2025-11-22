# Semantic Voice Transcriber (SVT)

**Multi-Komponenten Audio-Transkriptionssystem mit tiefer semantischer Analyse**

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by-nc-sa/4.0/)
[![Status](https://img.shields.io/badge/status-phase%202c%20complete-success.svg)]()

**Letzte Aktualisierung:** 2025-11-19 | **Commit:** 75fdfbbc

---

## 📋 Inhaltsverzeichnis

- [Überblick](#-überblick)
- [Hauptfunktionen](#-hauptfunktionen)
- [Systemarchitektur](#-systemarchitektur)
- [Installation](#-installation)
- [Schnellstart](#-schnellstart)
- [Verwendung](#-verwendung)
- [Komponenten-Referenz](#-komponenten-referenz)
- [Verzeichnisstruktur](#-verzeichnisstruktur)
- [Ausgabeformate](#-ausgabeformate)
- [Konfiguration](#-konfiguration)
- [API-Dokumentation](#-api-dokumentation)
- [Roadmap](#-roadmap)
- [Troubleshooting](#-troubleshooting)
- [Lizenz](#-lizenz)

---

## 🎯 Überblick

**Semantic Voice Transcriber (SVT)** ist ein hochentwickeltes Multi-Komponenten-System, das WhatsApp-Audio-Transkription mit tiefer semantischer Analyse kombiniert. Das System besteht aus drei Hauptsubsystemen:

### 🔧 Hauptsubsysteme

1. **WhisperSpeakerMatcher**: Audio-Transkription mit Sprechererkennung und Memory-basiertem Lernen
2. **Super Semantic Processor**: Semantische Analyse-Engine, die Chat-Historien in strukturierte semantische Repräsentationen transformiert
3. **Prosody Voice Marker System**: Prosodieanalyse für emotionale Wendepunkt-Erkennung

### 🎯 Anwendungsbereiche

- **Therapeutische Transkription**: Emotionale Wendepunkte in Therapiegesprächen
- **WhatsApp Chat-Analyse**: Automatische Transkription und semantische Verarbeitung
- **Speaker Learning**: Kontinuierliche Verbesserung der Sprecherprofile
- **Prosody Research**: Wissenschaftliche Analyse von Sprachmelodie und Rhythmus

### 📊 Kernstatistiken

- **13.000+** Zeilen Python-Code
- **50+** Hauptkomponenten
- **58** Test-Dateien (42 in tests/, 16 in root)
- **57** Dokumentationsdateien
- **5** Audio-Formate (.opus, .m4a, .wav, .mp3, .ogg)
- **5** Whisper-Modelle (tiny → large)
- **7** Emotionale Kategorien
- **4** Prosody-Features ("Big 4")
- **18** ATO Marker + **3** SEM Marker

---

## ✨ Hauptfunktionen

### Phase 1: Prosody-Extraktion ✅ Abgeschlossen

#### 🎵 Prosodische Merkmale ("Big 4")

| Feature | Beschreibung | Methode | Marker |
|---------|-------------|---------|--------|
| **Tempo** | Wörter pro Minute (WPM) | Word count / Duration | `[TEMPO↑/↓]` |
| **Tonhöhe (Pitch)** | F0-Analyse in Hz | Librosa PipTrack / Parselmouth | `[PITCH↑/↓]` |
| **Energie** | RMS und dB-Werte | Librosa RMS | `[ENERGY↑/↓]` |
| **Pausen** | Silence Detection >1s | VAD (Voice Activity Detection) | `[PAUSE]` |

#### 📊 Intelligente Baseline-Berechnung

- **Globale Baseline**: Berechnet pro Audio-Datei aus allen Segmenten
- **Running Average**: Kontinuierliche Aktualisierung in Sprecher-Profilen
- **Deviation Detection**: Automatische Erkennung signifikanter Abweichungen
  - Tempo: ±20% Schwelle
  - Pitch: ±15% Schwelle
  - Energie: ±25% Schwelle

#### 📝 Multi-Format-Ausgabe

1. **Annotiertes Markdown**: Therapeuten-freundlich mit Inline-Markern
2. **JSON Sidecar**: Strukturierte Daten für LLM-Verarbeitung
3. **HTML**: Farbcodierte Sprecher und Wendepunkte
4. **PDF**: Professioneller Export via WeasyPrint
5. **CSV**: Tabellarische Prosody-Daten für Data Science

### Phase 2a: Professional Layout & Export ✅ Abgeschlossen

- ✅ HTML-Export mit 6 Sprecher-Farben
- ✅ PDF-Export mit vollständiger Formatierung
- ✅ CSV-Export für statistische Analyse
- ✅ Emotionale Wendepunkt-Hervorhebung (orange)
- ✅ Farbige Prosody-Marker in allen Formaten

### Phase 2b: Automatische Sprechererkennung ✅ Abgeschlossen

- ✅ Speaker Diarization mit **pyannote.audio**
- ✅ Automatische Segmentierung (Speaker A, B, C, ...)
- ✅ GPU-Acceleration Support
- ✅ Hugging Face Model Integration
- ✅ Konfigurierbare Speaker-Anzahl (min: 1, max: 10)
- ✅ Timeline-basierte Speaker-Attribution
- ✅ Integration in alle Ausgabeformate

### 🚀 Intelligent Pipeline System

```
Audio Input
    ↓
[Quality Analysis]
    ├─ SNR (Signal-to-Noise Ratio)
    ├─ Clipping Detection
    ├─ Silence Ratio
    └─ Quality Score → Model Selection
    ↓
[Preprocessing] (if quality < 60)
    ├─ Noise Reduction
    ├─ Volume Normalization (-20dB)
    └─ High-Pass Filter (80 Hz)
    ↓
[Transcription]
    ├─ Whisper (adaptive model)
    ├─ DateTime Extraction
    ├─ Confidence Scoring
    └─ Emotional Marker Loading
    ↓
[Prosody Extraction]
    ├─ Pitch (F0)
    ├─ Tempo (WPM)
    ├─ Energy (RMS, dB)
    └─ Pause Detection
    ↓
[Speaker Recognition]
    ├─ Folder-based
    ├─ Memory-based
    └─ Diarization (optional)
    ↓
[Semantic Processing]
    ├─ FRAUSAR Markers
    ├─ CoSD Analysis
    └─ Emotional Arc
    ↓
[Memory Update]
    └─ Speaker Profile Evolution
    ↓
[Multi-Format Output]
    └─ MD / JSON / HTML / PDF / CSV
```

### 🧠 Memory-System (Speaker Learning)

Kontinuierliches Lernen über Sprecher:

```yaml
# Memory/{speaker}.yaml
keywords: [häufige Wörter]
topics: [Technologie: 45, Business: 23, Personal: 12]
voice_characteristics: [bedächtig, präzise, technisch_orientiert]
prosody_patterns:
  pitch_profile:
    mean_pitch: 147.8           # Hz (Running Average)
    pitch_variability: 19.4     # Standardabweichung
    sample_count: 15
  tempo_profile:
    mean_bpm: 118.5            # Beats per Minute
    mean_speech_rate: 4.3      # Silben/Sekunde
    sample_count: 15
  energy_profile:
    mean_energy: 0.045         # RMS Energy
    energy_variability: 0.012
    mean_dynamic_range: 0.28
    sample_count: 15
```

### 🎭 Emotionsanalyse

**Multi-Source Approach**:
1. **Audio-Features** (Librosa): Pitch-Variabilität, Energie, Tempo
2. **Text-Sentiment** (TextBlob): Polarity (-1 bis +1), Subjectivity (0 bis 1)
3. **Marker-System**: Emotionale Marker aus `ALL_SEMANTIC_MARKER_TXT/`

**7 Emotionale Kategorien**:
- 🌅 hoffnungsvoll_antreibend (Hopeful)
- 🔍 neugierig_forschend (Curious)
- 🌊 sehnsuchtsvoll_still (Longing)
- 💧 traurig_reflektierend (Sad)
- 🔥 wuetend_rebellisch (Angry)
- ✨ mystisch_symbolisch (Mystical)
- 🎉 begeistert_enthusiastisch (Enthusiastic)

---

## 🏗️ Systemarchitektur

### Schichtenmodell

```
┌─────────────────────────────────────────────────────────┐
│                  USER INTERFACES                        │
│  svt.py | super_semantic_gui.py | start_super_semantic  │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────┴────────────────────────────────────┐
│              ORCHESTRATION LAYER                        │
│    auto_transcriber_v4_emotion.py (WhisperSpeakerMatcherV4) │
│    - Koordiniert alle Processing-Schritte               │
│    - Managed Datenfluss zwischen Komponenten            │
└────────────────────┬────────────────────────────────────┘
                     │
   ┌─────────────────┼─────────────────┬──────────────┐
   │                 │                 │              │
┌──┴──────┐  ┌──────┴────┐  ┌────────┴────┐  ┌──────┴──────┐
│ANALYSIS │  │EXTRACTION │  │PROCESSING   │  │RECOGNITION  │
│LAYER    │  │LAYER      │  │LAYER        │  │LAYER        │
├─────────┤  ├───────────┤  ├─────────────┤  ├─────────────┤
│Audio    │  │Prosody    │  │Semantic     │  │Speaker      │
│Quality  │  │Analyzer   │  │Processor    │  │Diarizer     │
│Analyzer │  │Prosody    │  │Emotional    │  │             │
│Audio    │  │Extractor  │  │Analyzer     │  │             │
│Preproc  │  │Whisper    │  │ChatWeaver   │  │             │
└──┬──────┘  └─────┬─────┘  └──────┬──────┘  └──────┬──────┘
   │               │               │                │
   └───────────────┴───────────────┴────────────────┘
                   │
      ┌────────────┴────────────┐
      │   OUTPUT FORMATTER      │
      ├─────────────────────────┤
      │ Markdown + JSON Sidecar │
      │ HTML/PDF/CSV Export     │
      └────────────┬────────────┘
                   │
      ┌────────────┴────────────┐
      │    STORAGE LAYER        │
      ├─────────────────────────┤
      │ Transkripte_LLM/ (OUT)  │
      │ Memory/ (Profiles)      │
      │ Eingang/ (INPUT)        │
      └─────────────────────────┘
```

### Datenfluss-Diagramm

Siehe [CLAUDE.md](CLAUDE.md) Abschnitt 3.2 für detaillierten Datenfluss von Input → Output durch alle 11 Processing-Stages.

---

## 🔧 Installation

### Systemvoraussetzungen

- **Python**: 3.8+ (getestet mit 3.12.3)
- **OS**: Linux, macOS, Windows (WSL empfohlen)
- **RAM**: Minimum 8GB (16GB empfohlen für large Modell)
- **GPU**: Optional (CUDA-fähig für schnellere Verarbeitung)

### System-Dependencies

#### Linux (Ubuntu/Debian)

```bash
# FFmpeg (erforderlich für Audio-Konvertierung)
sudo apt install ffmpeg

# PortAudio (für Audio-I/O)
sudo apt install portaudio19-dev

# Python Development Headers
sudo apt install python3-dev python3-pip

# Tkinter (für GUI)
sudo apt install python3-tk
```

#### macOS

```bash
# FFmpeg
brew install ffmpeg

# PortAudio
brew install portaudio

# Tkinter ist bereits in Python enthalten
```

### Python-Pakete

#### Basis-Installation

```bash
pip3 install -r requirements.txt
```

**requirements.txt** enthält:
- openai-whisper >= 20230314 (Speech-to-Text)
- PyYAML >= 6.0 (Konfiguration)
- librosa >= 0.9.0 (Audio-Analyse)
- soundfile >= 0.10.0 (Audio-I/O)
- torch == 2.9.0 (Deep Learning Backend, kompatibel zu torchvision 0.24.0)
- packaging >= 24.2, < 25.0 (verhindert Konflikte mit Pinecone-Plugin-Abhängigkeiten)
- pillow >= 11.1.0, < 12.0.0 (kompatibel mit Streamlit & Together SDK)
- numpy >= 1.21.0 (Numerische Operationen)
- pathlib2 >= 2.3.7 (Pfad-Handling)
- watchdog >= 2.1.9 (File Watching)

#### Emotion-Analysis-Erweiterung

```bash
pip3 install -r requirements_emotion.txt
```

**Zusätzliche Pakete**:
- textblob >= 0.17.1 (Sentiment Analysis)
- scikit-learn >= 1.1.0 (Machine Learning)
- nltk >= 3.8 (Natural Language Processing)
- spacy >= 3.4.0 (NLP Framework)
- matplotlib >= 3.5.0 (Plotting)
- seaborn >= 0.11.0 (Statistical Visualization)

#### Speaker Diarization (Optional)

```bash
pip3 install pyannote.audio
```

**Hugging Face Token erforderlich**:

Siehe [SPEAKER_DIARIZATION.md](SPEAKER_DIARIZATION.md) für Setup-Details.

### Automatisches Setup

```bash
python3 setup_environment.py
```

Dieser Befehl:
1. Prüft alle System-Dependencies
2. Installiert fehlende Python-Pakete
3. Lädt NLTK-Daten herunter
4. Erstellt notwendige Verzeichnisse
5. Initialisiert Konfigurationsdateien

### FFmpeg-Verifikation

```bash
ffmpeg -version
```

Erwartete Ausgabe: FFmpeg Version-Info mit Codec-Unterstützung

---

## 🚀 Schnellstart

### 1. GUI starten (Empfohlen)

```bash
python3 svt.py
```

### 2. Quick Test durchführen

1. **Audio-Dateien vorbereiten**: Platziere `.opus`, `.m4a`, `.wav`, oder `.mp3` Dateien in `Eingang/Speaker_Name/`
2. **GUI öffnen**: `python3 svt.py`
3. **Quick Test klicken**: Verarbeitet erste Datei mit allen Features
4. **Ergebnis prüfen**: Öffne `Transkripte_LLM/*.md`

### 3. Beispiel-Workflow

```bash
# Schritt 1: Verzeichnisstruktur vorbereiten
mkdir -p Eingang/Patient1/
cp meine_audio.m4a Eingang/Patient1/

# Schritt 2: GUI starten
python3 svt.py

# Schritt 3: In der GUI
# - Input: Eingang/
# - Output: Transkripte_LLM/
# - Features: ✓ Emotions ✓ Prosody ✓ Memory
# - Klicke "🧪 Quick Test"

# Schritt 4: Ergebnis anzeigen
cat Transkripte_LLM/2025-11-12_14-30-45_Patient1_transkript.md
```

### 4. Alternative: Kommandozeile

```bash
# V3: Basic Transcription
python3 auto_transcriber_v3.py --local

# V4: Mit Emotionen
python3 auto_transcriber_v4_emotion.py

# Semantische Analyse
python3 start_super_semantic.py
```

---

## 📖 Verwendung

### GUI-Modus (svt.py)

#### Hauptfenster

```
┌─────────────────────────────────────────────────────────┐
│   Semantic Voice Transcriber (SVT)                      │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  📁 Konfiguration                                       │
│    Input:  [Eingang/           ] [Browse]              │
│    Output: [Transkripte_LLM/   ] [Browse]              │
│    Memory: [Memory/            ] [Browse]              │
│                                                         │
│  🎛️ Whisper Modell                                     │
│    ⚪ tiny   ⚪ base   ⚫ small   ⚪ medium   ⚪ large    │
│                                                         │
│  ✅ Features                                            │
│    ☑ Emotions-Analyse                                  │
│    ☑ Prosody-Extraktion                                │
│    ☑ Memory-System                                     │
│    ☑ Speaker Diarization (erfordert HF Token)          │
│                                                         │
│  🎯 Aktionen                                            │
│    [🚀 Transkription starten]                          │
│    [🧪 Quick Test]                                     │
│    [🎵 Prosody Test (30s)]                             │
│                                                         │
│  📊 Progress                                            │
│    [████████░░] 80% - Processing file 4/5...           │
│                                                         │
│  📝 Log                                                 │
│    [2025-11-12 14:30:45] Quality Score: 78.5           │
│    [2025-11-12 14:30:46] Selected model: small         │
│    [2025-11-12 14:30:50] Transcription complete        │
│    [2025-11-12 14:30:52] Prosody extracted: 24 segs    │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

#### Feature-Beschreibungen

**Emotions-Analyse**:
- Aktiviert TextBlob Sentiment-Analyse
- Lädt emotionale Marker aus Marker-System
- Berechnet dominante Emotion pro Transkript

**Prosody-Extraktion**:
- Extrahiert Big 4 Features (Tempo, Pitch, Energie, Pausen)
- Berechnet Baselines und Deviationen
- Erzeugt annotierte Markdown-Ausgabe mit Inline-Markern

**Memory-System**:
- Erstellt/aktualisiert Sprecher-Profile in `Memory/{speaker}.yaml`
- Baut kontinuierlich Prosody-Baselines auf
- Lernt Sprecher-Charakteristiken

**Speaker Diarization**:
- Automatische Erkennung mehrerer Sprecher
- Labels: Speaker A, B, C, D, ...
- Erfordert Hugging Face Token (siehe Setup)

#### Button-Funktionen

**🚀 Transkription starten**:
- Verarbeitet alle Audio-Dateien in Input-Verzeichnis
- Batch-Processing mit Progress-Anzeige
- Erstellt Ausgaben für jede Datei

**🧪 Quick Test**:
- One-Click Test für erste Audio-Datei
- Vollständige Verarbeitung mit allen aktivierten Features
- Zeigt Qualitätsanalyse im Log

**🎵 Prosody Test (30s)**:
- Extrahiert erste 30 Sekunden der ersten Datei
- Schneller Test der Prosody-Pipeline
- Erzeugt annotiertes Markdown + JSON Sidecar

### Kommandozeilen-Modi

#### V3: Basic Transcription + DateTime Extraction

```bash
python3 auto_transcriber_v3.py --local
```

**Features**:
- Whisper Transkription
- DateTime Extraction aus WhatsApp-Dateinamen
- Folder-basierte Speaker-Erkennung
- Memory Profile Loading/Creation
- Output: `.md` Dateien mit Metadaten

**WhatsApp Filename Pattern**:
```
WhatsApp Audio YYYY-MM-DD at HH.MM.SS.opus
```

#### V4: Emotional Analysis + Prosody

```bash
python3 auto_transcriber_v4_emotion.py
```

**Extends V3 mit**:
- Emotionale Marker-Analyse
- TextBlob Sentiment
- Librosa Audio-Features
- Prosody Integration
- Optional: Speaker Diarization
- Confidence Scoring

#### Semantic Analysis GUI

```bash
python3 super_semantic_gui.py
```

**Funktionalität**:
- WhatsApp-Export (.txt) Verarbeitung
- Transkript-Ordner Integration
- Marker-Set Selection (All_Markers, Trauma, Custom)
- Semantic Thread Identification
- Emotional Arc Calculation
- Output: JSON + Markdown Summary

#### Mode Launcher

```bash
python3 start_super_semantic.py
```

**Modi**:
1. **GUI-Modus**: Startet `super_semantic_gui.py`
2. **CLI-Modus**: Interaktive Kommandozeilen-Prompts
3. **Demo-Modus**: Erstellt Sample-Daten und führt vollständige Pipeline aus
4. **Help-Modus**: Zeigt Dokumentation

---

## 🧩 Komponenten-Referenz

### Transkriptionssysteme

| Komponente | Version | Hauptklasse | Zweck |
|------------|---------|-------------|-------|
| `auto_transcriber_v3.py` | V3 | `WhisperSpeakerMatcherV3` | Basis + DateTime |
| `auto_transcriber_v4_emotion.py` | V4 | `WhisperSpeakerMatcherV4` | + Emotions + Prosody |
| `svt.py` | Latest | `SemanticVoiceTranscriberGUI` | Professional GUI |
| `whisper_transcriber.py` | Legacy | `WhisperTranscriber` | Basis-Wrapper |

### Prosodieanalyse

| Komponente | Klasse | Funktion |
|------------|--------|----------|
| `prosody_analyzer.py` | `ProsodyAnalyzer` | Extrahiert Pitch, Tempo, Energie |
| `prosody_extractor.py` | `ProsodyExtractor` | Big 4 Features pro Segment |
| `prosody_extractor.py` | `ProsodyBaseline` | Baseline-Berechnung & Deviations |
| `prosody_extractor.py` | `ProsodyFeatures` | Dataclass für Features |

**Verwendung**:

```python
from prosody_analyzer import ProsodyAnalyzer

analyzer = ProsodyAnalyzer()
prosody = analyzer.extract_from_file('audio.wav')

print(f"Pitch: {prosody.pitch_mean_hz:.1f} Hz")
print(f"Tempo: {prosody.tempo_wpm:.1f} WPM")
print(f"Energy: {prosody.energy_rms:.4f}")
```

### Sprechererkennung

| Komponente | Klasse | Technologie |
|------------|--------|-------------|
| `speaker_diarizer.py` | `SpeakerDiarizer` | pyannote.audio |

**Features**:
- Automatische Speaker-Segmentierung
- GPU-Acceleration
- Hugging Face Model: `pyannote/speaker-diarization-3.1`
- Konfigurierbare Min/Max Speaker (1-10)

**Verwendung**:

```python
from speaker_diarizer import SpeakerDiarizer

diarizer = SpeakerDiarizer()
speaker_timeline = diarizer.process_file(
    'audio.wav',
    min_speakers=1,
    max_speakers=5
)

for segment, _, speaker in speaker_timeline.itertracks(yield_label=True):
    print(f"{segment.start:.1f}s - {segment.end:.1f}s: {speaker}")
```

### Audioqualität & Vorverarbeitung

| Komponente | Klasse | Funktionen |
|------------|--------|------------|
| `audio_quality_analyzer.py` | `AudioQualityAnalyzer` | SNR, Clipping, Silence, Quality Score |
| `audio_preprocessor.py` | `AudioPreprocessor` | Noise Reduction, Normalization, Filter |

**Quality Score Berechnung**:

```python
from audio_quality_analyzer import AudioQualityAnalyzer

analyzer = AudioQualityAnalyzer()
quality = analyzer.analyze_file('audio.wav')

print(f"SNR: {quality['snr']:.1f} dB")
print(f"Clipping: {quality['clipping_percentage']:.2f}%")
print(f"Silence: {quality['silence_ratio']:.2f}%")
print(f"Quality Score: {quality['quality_score']:.1f}/100")

# Empfohlenes Whisper-Modell basierend auf Qualität
model = analyzer.recommend_model(quality['quality_score'])
```

**Preprocessing**:

```python
from audio_preprocessor import AudioPreprocessor

preprocessor = AudioPreprocessor()
clean_audio = preprocessor.process_file(
    'noisy_audio.wav',
    noise_reduction=True,
    normalize=True,
    high_pass_filter=True
)
```

### Semantische Verarbeitung

| Komponente | Klasse | Zweck |
|------------|--------|-------|
| `super_semantic_processor.py` | `SuperSemanticProcessor` | Marker-Integration, CoSD |
| `semantic_chat_weaver.py` | `SemanticChatWeaver` | Chat → Semantic Nodes |
| `integrated_semantic_weaver.py` | `IntegratedSemanticWeaver` | Multi-System Kombination |

**Dataclasses**:

```python
@dataclass
class SemanticMessage:
    id: str
    timestamp: datetime
    sender: str
    content: str
    type: str  # text, audio, image, document
    emotion: Dict[str, float]
    markers: List[str]
    semantic_scores: Dict[str, float]
    metadata: Dict[str, Any]
```

### Output-Formatierung

| Komponente | Klasse | Formate |
|------------|--------|---------|
| `output_formatter.py` | `OutputFormatter` | Markdown + JSON Sidecar |
| `html_formatter.py` | `HTMLFormatter` | HTML, PDF, CSV |

**Verwendung**:

```python
from output_formatter import OutputFormatter

formatter = OutputFormatter()
formatter.format_transcript(
    transcript="...",
    prosody_features=[...],
    output_file="transkript.md"
)
```

### Memory-System

| Komponente | Klasse | Zweck |
|------------|--------|-------|
| `build_memory_from_transcripts.py` | `MemoryBuilder` | Profile Creation/Update |

**Memory-Struktur** (`Memory/{speaker}.yaml`):

```yaml
keywords: [häufige, wörter, liste]
topics:
  technology: 45
  business: 23
  personal: 12
voice_characteristics: [bedächtig, präzise, technisch_orientiert]
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
metadata:
  name: "Speaker Name"
  last_updated: "2025-11-12T14:30:45"
  total_interactions: 42
interactions:
  - timestamp: "2025-11-12T10:15:30"
    file: "2025-11-12_10-15-30_speaker_transkript.md"
    topics: [technology, business]
```

---

## 📂 Verzeichnisstruktur

```
Semantic_Voice_Transcriber/
│
├── 📁 ROOT LEVEL PYTHON FILES
│   │
│   ├── ENTRY POINTS (GUI/CLI)
│   │   ├── svt.py ............................ Main Professional GUI
│   │   ├── start_super_semantic.py ........... Mode Launcher
│   │   ├── super_semantic_gui.py ............. Semantic Analysis GUI
│   │   └── run_local.py ...................... Local Mode Runner
│   │
│   ├── TRANSCRIPTION ENGINES
│   │   ├── auto_transcriber_v3.py ............ V3: Basic + DateTime
│   │   ├── auto_transcriber_v4_emotion.py .... V4: + Emotions + Prosody
│   │   ├── whisper_transcriber.py ............ Legacy Wrapper
│   │   └── whisper_auto_runner.py ............ Auto-execution Runner
│   │
│   ├── PROSODY ANALYSIS (Voice-Marker 2.0)
│   │   ├── prosody_analyzer.py ............... ProsodyAnalyzer Class
│   │   ├── prosody_extractor.py .............. ProsodyExtractor + Big 4
│   │   ├── output_formatter.py ............... Markdown/JSON Formatter
│   │   └── html_formatter.py ................. HTML/PDF/CSV Export
│   │
│   ├── SPEAKER RECOGNITION
│   │   ├── speaker_diarizer.py ............... SpeakerDiarizer (pyannote)
│   │   └── initialize_person.py .............. Speaker Initialization
│   │
│   ├── AUDIO PROCESSING
│   │   ├── audio_quality_analyzer.py ......... Quality Score Calculation
│   │   ├── audio_preprocessor.py ............. Noise Reduction & Normalization
│   │   └── task3_requirements_check.py ....... Dependency Validator
│   │
│   ├── SEMANTIC INTEGRATION
│   │   ├── super_semantic_processor.py ....... Main Semantic Engine
│   │   ├── semantic_chat_weaver.py ........... Chat → Semantic Nodes
│   │   ├── integrated_semantic_weaver.py ..... Combined System
│   │   └── build_memory_from_transcripts.py .. Memory Builder
│   │
│   ├── GOOGLE DRIVE
│   │   └── google_drive_sync.py .............. Drive Synchronization
│   │
│   ├── UTILITIES
│   │   ├── code_quality_review.py ............ Code Review Tool
│   │   └── setup_environment.py .............. Environment Setup
│   │
│   └── TEST SUITE (12 Files)
│       ├── test_prosody_analyzer.py
│       ├── test_prosody_pipeline.py
│       ├── test_transcriber_v4_prosody.py
│       ├── test_audio_preprocessor.py
│       ├── test_audio_quality_analyzer.py
│       ├── test_confidence_scoring.py
│       ├── test_initialize_person.py
│       ├── test_integration_therapeutic.py
│       ├── test_intelligent_pipeline_integration.py
│       ├── test_memory_prosody.py
│       ├── test_task3_integration.py
│       ├── test_yaml_structure.py
│       └── run_test_prosody.py ............... Test Runner
│
├── 📁 Eingang/ ............................. INPUT DIRECTORY
│   ├── {speaker1}/ ......................... Speaker-specific Folder
│   │   ├── WhatsApp Audio 2025-11-12 at 14.30.45.opus
│   │   ├── recording.m4a
│   │   └── *.wav, *.mp3, *.ogg
│   ├── {speaker2}/
│   └── ... (beliebig viele Sprecher)
│
├── 📁 Memory/ ............................. SPEAKER PROFILES
│   ├── PSG.yaml ............................ Profile Template
│   ├── PSG001.yaml ......................... Profile Instance
│   ├── {speaker1}.yaml ..................... Auto-created Profiles
│   └── {speaker2}.yaml
│
├── 📁 Transkripte_LLM/ ................... OUTPUT DIRECTORY
│   ├── 2025-11-12_14-30-45_speaker_transkript.md
│   ├── 2025-11-12_14-30-45_speaker_transkript.prosody.json
│   ├── 2025-11-12_14-30-45_speaker_transkript.html
│   ├── 2025-11-12_14-30-45_speaker_transkript.pdf
│   └── 2025-11-12_14-30-45_speaker_transkript.csv
│
├── 📁 docs/ ............................... DOCUMENTATION
│   ├── INTELLIGENT_PIPELINE.md ............. Pipeline Design
│   ├── THERAPEUTIC_TRANSCRIPTION_GUIDE.md
│   └── plans/
│       └── 2025-11-10-therapeutic-transcription-system.md
│
├── 📁 utilities/ .......................... HELPER SCRIPTS
│   └── merge_transcripts.py ............... Transcript Merger
│
├── 📁 TextBlob/ ........................... LOCAL TEXTBLOB
│   └── (lokale TextBlob Installation)
│
├── 🔧 CONFIGURATION FILES
│   ├── requirements.txt ................... Base Dependencies
│   ├── requirements_emotion.txt ........... Emotion Dependencies
│   ├── CLAUDE.md .......................... AI Instructions (Project Guide)
│   └── setup_environment.py ............... Auto-setup Script
│
└── 📚 DOCUMENTATION FILES
    ├── README.md .......................... Main Documentation (this file)
    ├── VERSION_STATUS.md .................. Version Status & Roadmap
    ├── README_SUPER_SEMANTIC.md ........... Semantic System Details
    ├── ANLEITUNG_NUTZUNG.md ............... Usage Guide (German)
    ├── ORDNER_ANLEITUNG.md ................ Folder Structure Guide
    ├── SPEAKER_DIARIZATION.md ............. Diarization Setup & Details
    ├── SCHNELLERE_ALTERNATIVEN.md ......... Faster Alternatives
    ├── TASK3_CODE_REVIEW_REPORT.md ........ Code Review Report
    ├── TASK5_IMPLEMENTATION_SUMMARY.md .... Implementation Summary
    └── Lizenz: Creative Commons BY-NC-SA 4.0.md
```

---

## 📤 Ausgabeformate

### 1. Annotiertes Markdown (.md)

**Zweck**: Therapeuten-freundliche Lesbarkeit mit Inline-Prosody-Markern

**Beispiel**:

```markdown
# Transkript: WhatsApp Audio 2025-11-12 at 14.30.45.opus

**Chat mit:** Patient1
**Aufnahme am:** 12.11.2025 um 14:30:45
**Verarbeitet am:** 12.11.2025 um 14:35:22
**Original-Datei:** WhatsApp Audio 2025-11-12 at 14.30.45.opus

**Dominante Emotion:** begeistert_enthusiastisch 🎉
**Emotionale Valenz:** 0.87

## Qualitätsanalyse
- **SNR**: 22.3 dB (gut)
- **Clipping**: 0.5%
- **Silence Ratio**: 15.2%
- **Quality Score**: 78.5/100

## Prosody-Baseline
- **Tempo**: 187.7 WPM
- **Tonhöhe**: 199.8 Hz
- **Energie**: 0.0792

## Transkription

**[00:00 - 00:02]** Okay, lass uns mal schauen.
  *Tempo: 176.5 WPM (-6.0%) | Tonhöhe: 195.3 Hz (-2.3%) | Energie: 0.0745 (-5.9%)*

**[00:05 - 00:07]** So, wir haben ja nicht so viel Zeit. `[TEMPO↑]`
  *Tempo: 226.4 WPM (+20.6%) | Tonhöhe: 226.0 Hz (+13.2%) | Energie: 0.0836 (+5.5%)*

**[00:07 - 00:08]** Wolli, wir müssen sprechen! `[TEMPO↑]`
  *Tempo: 272.7 WPM (+45.3%) | Tonhöhe: 211.2 Hz (+5.8%)*

**[00:19 - 00:21]** Wolli, we need to talk. `[PITCH↓]` `[ENERGY↓]` `[PAUSE]`
  *Tempo: 182.9 WPM (-2.5%) | Tonhöhe: 168.7 Hz (-15.5%) | Energie: 0.0497 (-37.3%)*

## Kontext für LLM

Diese Audio-Nachricht wurde am 12.11.2025 um 14:30:45 aufgenommen.
Sie enthält 24 Segmente mit insgesamt 3 signifikanten Prosodieabweichungen.
Dominante Emotion: begeistert_enthusiastisch mit Valenz 0.87.
```

### 2. JSON Sidecar (.prosody.json)

**Zweck**: Strukturierte Daten für LLM-Verarbeitung & Data Science

**Schema**:

```json
{
  "metadata": {
    "file": "WhatsApp Audio 2025-11-12 at 14.30.45.opus",
    "speaker": "Patient1",
    "recording_datetime": "2025-11-12T14:30:45",
    "processing_datetime": "2025-11-12T14:35:22",
    "duration_seconds": 125.3,
    "dominant_emotion": "begeistert_enthusiastisch",
    "emotional_valence": 0.87
  },
  "quality": {
    "snr_db": 22.3,
    "clipping_percentage": 0.5,
    "silence_ratio": 0.152,
    "quality_score": 78.5,
    "whisper_model": "small"
  },
  "baseline": {
    "tempo_wpm_mean": 187.7,
    "tempo_wpm_std": 28.4,
    "pitch_mean_hz": 199.8,
    "pitch_std_hz": 24.1,
    "energy_rms_mean": 0.0792,
    "energy_rms_std": 0.0156
  },
  "segments": [
    {
      "index": 0,
      "start_time": 0.0,
      "end_time": 2.1,
      "duration": 2.1,
      "text": "Okay, lass uns mal schauen.",
      "tempo_wpm": 176.5,
      "tempo_deviation_pct": -6.0,
      "pitch_mean_hz": 195.3,
      "pitch_deviation_pct": -2.3,
      "energy_rms": 0.0745,
      "energy_deviation_pct": -5.9,
      "pause_before_ms": 0,
      "pause_after_ms": 0,
      "markers": [],
      "confidence": 0.92
    },
    {
      "index": 1,
      "start_time": 5.2,
      "end_time": 7.4,
      "duration": 2.2,
      "text": "So, wir haben ja nicht so viel Zeit.",
      "tempo_wpm": 226.4,
      "tempo_deviation_pct": 20.6,
      "pitch_mean_hz": 226.0,
      "pitch_deviation_pct": 13.2,
      "energy_rms": 0.0836,
      "energy_deviation_pct": 5.5,
      "pause_before_ms": 0,
      "pause_after_ms": 0,
      "markers": ["TEMPO↑"],
      "confidence": 0.88
    }
  ],
  "statistics": {
    "total_segments": 24,
    "marked_segments": 3,
    "average_confidence": 0.91,
    "low_confidence_segments": 1
  }
}
```

### 3. HTML Export (.html)

**Zweck**: Farbcodierte Sprecher & Emotionale Wendepunkte

**Features**:
- **6 Sprecher-Farben**: Blau, Grün, Orange, Lila, Teal, Rosa
- **Wendepunkt-Hervorhebung**: Orange Hintergrund für signifikante Prosodieabweichungen
- **Farbige Prosody-Marker**: Grün (↑), Rot (↓), Gelb (PAUSE)
- **Responsive Design**: Mobile-friendly

### 4. PDF Export (.pdf)

**Zweck**: Professioneller Druck/Archivierung

**Technologie**: WeasyPrint (HTML → PDF)

**Layout**:
- A4 Format
- Vollständige Farbcodierung erhalten
- Kopf-/Fußzeilen mit Metadaten
- Seitenumbruch-Optimierung

### 5. CSV Export (.csv)

**Zweck**: Statistische Analyse & Data Science

**Spalten**:
```csv
segment_index,start_time,end_time,duration,text,speaker,tempo_wpm,tempo_deviation_pct,pitch_mean_hz,pitch_deviation_pct,energy_rms,energy_deviation_pct,pause_before_ms,pause_after_ms,markers,confidence
0,0.0,2.1,2.1,"Okay, lass uns mal schauen.",Speaker A,176.5,-6.0,195.3,-2.3,0.0745,-5.9,0,0,,0.92
1,5.2,7.4,2.2,"So, wir haben ja nicht so viel Zeit.",Speaker A,226.4,20.6,226.0,13.2,0.0836,5.5,0,0,TEMPO↑,0.88
```

---

## ⚙️ Konfiguration

### Whisper-Modell-Auswahl

| Modell | Parameter | RAM | VRAM (GPU) | Geschwindigkeit | Genauigkeit |
|--------|-----------|-----|------------|----------------|-------------|
| tiny | 39M | 1GB | 1GB | ⚡⚡⚡⚡⚡ | ⭐⭐ |
| base | 74M | 1GB | 1GB | ⚡⚡⚡⚡ | ⭐⭐⭐ |
| small | 244M | 2GB | 2GB | ⚡⚡⚡ | ⭐⭐⭐⭐ |
| medium | 769M | 5GB | 5GB | ⚡⚡ | ⭐⭐⭐⭐⭐ |
| large | 1550M | 10GB | 10GB | ⚡ | ⭐⭐⭐⭐⭐ |

**Automatische Auswahl** (Quality-basiert):
- Quality Score > 80: tiny/base
- Quality Score 60-80: small
- Quality Score < 60: medium (nach Preprocessing)

### Prosody-Schwellwerte

**Konfigurierbar in Code**:

```python
# prosody_extractor.py
TEMPO_THRESHOLD = 0.20    # ±20%
PITCH_THRESHOLD = 0.15    # ±15%
ENERGY_THRESHOLD = 0.25   # ±25%
PAUSE_THRESHOLD_MS = 1000 # >1000ms
```

### Speaker Diarization

**Hugging Face Token Setup**:

```bash
# Option 1: Environment Variable
export HF_TOKEN="hf_xxxxxxxxxxxxxxxxxxxxx"

# Option 2: .env File
echo "HF_TOKEN=hf_xxxxxxxxxxxxxxxxxxxxx" > .env

# Option 3: Code
import os
os.environ['HF_TOKEN'] = 'hf_xxxxxxxxxxxxxxxxxxxxx'
```

**Token erhalten**: https://huggingface.co/settings/tokens

### Google Drive Sync (Optional)

**Konfiguration** (`google_drive_sync.py`):

```python
DRIVE_PATHS = {
    'eingang': '/path/to/Drive/Eingang/',
    'memory': '/path/to/Drive/Memory/',
    'output': '/path/to/Drive/Transkripte_LLM/'
}
```

**Verwendung**:

```bash
python3 google_drive_sync.py --sync-all
```

---

## 📚 API-Dokumentation

### ProsodyAnalyzer

```python
class ProsodyAnalyzer:
    def extract_from_file(self, audio_path: str) -> Dict[str, Any]:
        """
        Extrahiert Prosody-Features aus Audio-Datei.

        Args:
            audio_path: Pfad zur Audio-Datei

        Returns:
            Dict mit:
              - pitch_mean_hz: Durchschnittliche Tonhöhe
              - pitch_std_hz: Standardabweichung Tonhöhe
              - tempo_bpm: Tempo in Beats per Minute
              - energy_rms: RMS Energie
              - energy_db: Energie in Dezibel
        """
```

### ProsodyExtractor

```python
class ProsodyExtractor:
    def extract_features(
        self,
        audio_path: str,
        segments: List[Dict]
    ) -> Tuple[List[ProsodyFeatures], ProsodyBaseline]:
        """
        Extrahiert Big 4 Features für alle Segmente.

        Args:
            audio_path: Pfad zur Audio-Datei
            segments: Whisper-Segmente mit start/end/text

        Returns:
            Tuple von:
              - List[ProsodyFeatures]: Features pro Segment
              - ProsodyBaseline: Globale Baseline
        """
```

### SpeakerDiarizer

```python
class SpeakerDiarizer:
    def __init__(self, use_auth_token: Optional[str] = None):
        """
        Initialisiert Speaker Diarization Pipeline.

        Args:
            use_auth_token: Hugging Face Token (optional, falls in ENV)
        """

    def process_file(
        self,
        audio_path: str,
        min_speakers: int = 1,
        max_speakers: int = 10
    ) -> Any:
        """
        Segmentiert Audio nach Sprechern.

        Args:
            audio_path: Pfad zur Audio-Datei
            min_speakers: Minimale Anzahl erwarteter Sprecher
            max_speakers: Maximale Anzahl erwarteter Sprecher

        Returns:
            pyannote.core.Annotation: Speaker Timeline
        """
```

### AudioQualityAnalyzer

```python
class AudioQualityAnalyzer:
    def analyze_file(self, audio_path: str) -> Dict[str, float]:
        """
        Analysiert Audio-Qualität.

        Returns:
            Dict mit:
              - snr_db: Signal-to-Noise Ratio
              - clipping_percentage: % geclippte Samples
              - silence_ratio: Anteil Stille
              - quality_score: Gesamt-Score (0-100)
        """

    def recommend_model(self, quality_score: float) -> str:
        """
        Empfiehlt Whisper-Modell basierend auf Qualität.

        Returns:
            Modellname: "tiny", "base", "small", "medium", "large"
        """
```

### OutputFormatter

```python
class OutputFormatter:
    def format_transcript(
        self,
        transcript: str,
        prosody_features: List[ProsodyFeatures],
        baseline: ProsodyBaseline,
        output_file: str,
        metadata: Dict[str, Any]
    ) -> None:
        """
        Erstellt annotiertes Markdown + JSON Sidecar.

        Args:
            transcript: Vollständiger Transkript-Text
            prosody_features: Liste von Prosody-Features
            baseline: Globale Baseline
            output_file: Ziel-Pfad (ohne Extension)
            metadata: Zusätzliche Metadaten
        """
```

---

## 🗺️ Roadmap

### ✅ Phase 1: Prosody-Extraktion (Abgeschlossen)

- [x] Big 4 Features: Tempo, Pitch, Energie, Pausen
- [x] Baseline-Berechnung & Deviation Detection
- [x] Annotiertes Markdown mit Inline-Markern
- [x] JSON Sidecar für strukturierte Daten
- [x] Integration mit Whisper Segmenten

### ✅ Phase 2a: Professional Layout & Export (Abgeschlossen)

- [x] HTML-Export mit farbcodierten Sprechern
- [x] PDF-Export via WeasyPrint
- [x] CSV-Export für Datenanalyse
- [x] Emotionale Wendepunkt-Hervorhebung
- [x] Farbige Prosody-Marker in allen Formaten

### ✅ Phase 2b: Speaker Diarization (Abgeschlossen)

- [x] Automatische Sprechererkennung mit pyannote.audio
- [x] Speaker A, B, C Labels
- [x] GPU-Acceleration Support
- [x] Integration in alle Ausgabeformatsysteme
- [x] Hugging Face Model Integration
- [x] Farbcodierte Sprecher (6 Farben)

### 🔄 Phase 2c: ATO-Marker-Integration (In Planung)

- [ ] VP_ATO/*.yaml Marker laden
- [ ] Prosodieabweichungen mit ATO-Markern verknüpfen
- [ ] Echtzeit-Marker-Trigger beim Transkribieren
- [ ] ATO → SEM → CLU → MEMA Hierarchie
- [ ] Wendepunkt-Erkennung für Therapeuten
- [ ] GUI-Integration für Speaker Diarization Controls

**Ziel**: Therapeutische Marker automatisch bei Prosodieabweichungen setzen

### 🚀 Phase 3: Streaming & Real-Time (Future)

- [ ] Live-Transkription mit Prosody
- [ ] WebSocket-Interface für externe Tools
- [ ] Echtzeit-Marker-Anzeige in GUI
- [ ] Stream-Processing Pipeline
- [ ] Low-Latency Mode (< 500ms)

### 🌐 Phase 4: Multi-Language & Advanced Features (Future)

- [ ] Multi-Language Support (DE, EN, FR, ES, IT)
- [ ] Sprachcode-Switching Erkennung
- [ ] Dialekt-Erkennung
- [ ] Akzent-Analyse
- [ ] Cross-Cultural Prosody-Baselines

### 🧠 Phase 5: Advanced AI Integration (Future)

- [ ] LLM-basierte semantische Threadidentifikation
- [ ] Automatische Zusammenfassung mit Wendepunkten
- [ ] Emotionale Arc Visualization
- [ ] Therapeutic Insight Generation
- [ ] Voice-Cloning für anonymisierte Demos

---

## 🔧 Troubleshooting

### Häufige Probleme

#### 1. FFmpeg nicht gefunden

**Symptom**:
```
FileNotFoundError: [Errno 2] No such file or directory: 'ffmpeg'
```

**Lösung**:
```bash
# Linux
sudo apt install ffmpeg

# macOS
brew install ffmpeg

# Verifikation
ffmpeg -version
```

#### 2. Tkinter nicht verfügbar

**Symptom**:
```
ImportError: No module named 'tkinter'
```

**Lösung**:
```bash
# Linux
sudo apt install python3-tk

# macOS: Bereits in Python enthalten
```

#### 3. Whisper-Modell Download schlägt fehl

**Symptom**:
```
URLError: <urlopen error [Errno -3] Temporary failure in name resolution>
```

**Lösung**:
- Internetverbindung prüfen
- Proxy/Firewall-Einstellungen prüfen
- Manueller Download: https://github.com/openai/whisper/discussions/63

#### 4. Speaker Diarization: HF Token Error

**Symptom**:
```
ValueError: The repository for pyannote/speaker-diarization-3.1 is gated. You must be authenticated to access it.
```

**Lösung**:
1. Hugging Face Account erstellen
2. Token erstellen: https://huggingface.co/settings/tokens
3. Model Access Request: https://huggingface.co/pyannote/speaker-diarization-3.1
4. Token als ENV Variable setzen:
   ```bash
   export HF_TOKEN="hf_xxxxxxxxxxxxxxxxxxxxx"
   ```

#### 5. GPU nicht erkannt

**Symptom**:
```
CUDA not available, using CPU
```

**Lösung**:
```bash
# CUDA Installation prüfen
nvidia-smi

# PyTorch mit CUDA neu installieren
pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

#### 6. Memory-Profil fehlt

**Symptom**:
```
FileNotFoundError: Memory/speaker.yaml not found
```

**Lösung**:
```bash
# Sprecher initialisieren
python3 initialize_person.py speaker_name

# Oder: Automatische Erstellung beim ersten Transkript
python3 auto_transcriber_v3.py --local
```

#### 7. Audio-Qualität zu niedrig

**Symptom**:
```
Quality Score: 35.2/100 - Very Poor
```

**Lösung**:
- Aktiviere **Audio Preprocessing** in GUI
- Nutze höheres Whisper-Modell (medium/large)
- Original-Aufnahme in besserer Qualität wiederholen

#### 8. JSON Parsing Error

**Symptom**:
```
json.decoder.JSONDecodeError: Expecting value: line 1 column 1
```

**Lösung**:
- Datei manuell prüfen: `cat file.json`
- Backup wiederherstellen
- Erneut transkribieren

---

## 📄 Lizenz

**Creative Commons BY-NC-SA 4.0**

Dieses Werk ist lizenziert unter einer [Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License](https://creativecommons.org/licenses/by-nc-sa/4.0/).

**Sie dürfen**:
- **Teilen**: Material kopieren und weiterverbreiten in jedem Format
- **Bearbeiten**: Material remixen, verändern und darauf aufbauen

**Unter folgenden Bedingungen**:
- **Namensnennung**: Angemessene Urheber- und Rechteangabe
- **Nicht kommerziell**: Keine kommerzielle Nutzung
- **Weitergabe unter gleichen Bedingungen**: Bei Remix unter gleicher Lizenz

**Copyright**: DYAI 2025

---

## 🙏 Credits & Danksagungen

### Technologien

- **[OpenAI Whisper](https://github.com/openai/whisper)**: State-of-the-Art Speech Recognition
- **[Librosa](https://librosa.org/)**: Audio Analysis Library
- **[Parselmouth](https://parselmouth.readthedocs.io/)**: Praat Python Interface
- **[pyannote.audio](https://github.com/pyannote/pyannote-audio)**: Speaker Diarization
- **[TextBlob](https://textblob.readthedocs.io/)**: Sentiment Analysis
- **[WeasyPrint](https://weasyprint.org/)**: PDF Generation
- **[PyTorch](https://pytorch.org/)**: Deep Learning Framework

### Entwicklung

- **Claude Code (Anthropic)**: Development Assistant & Code Generation
- **DYAI Framework**: Therapeutische Marker-Systeme (LD3.x, ATO/SEM/CLU/MEMA)

### Marker-Systeme

- **FRAUSAR**: 63+ Semantic Markers
- **CoSD/MARSAP**: Context-of-Semantic Drift Analysis
- **VP_ATO**: Atomic Voice Markers (Phase 2c)
- **Marker_LD3.5_SSoTh**: 4-Tier Therapeutic Marker System

---

## 📞 Support & Kontakt

### Dokumentation

- **Main README**: [README.md](README.md) (dieses Dokument)
- **Version Status**: [VERSION_STATUS.md](VERSION_STATUS.md)
- **Claude AI Guide**: [CLAUDE.md](CLAUDE.md)
- **Speaker Diarization**: [SPEAKER_DIARIZATION.md](SPEAKER_DIARIZATION.md)
- **Usage Guide**: [ANLEITUNG_NUTZUNG.md](ANLEITUNG_NUTZUNG.md)

### Tests durchführen

```bash
# Alle Tests
python3 -m pytest test_*.py -v

# Spezifische Test-Suite
python3 test_prosody_pipeline.py
python3 -m pytest test_integration_therapeutic.py -v
```

### Logs prüfen

```bash
# Transkriptions-Log
tail -f transcription.log

# V4 Emotion Log
tail -f transcription_v4_emotion.log
```

---

## 🚀 Zusammenfassung

**Semantic Voice Transcriber (SVT)** ist ein hochentwickeltes System zur therapeutischen Audio-Transkription mit:

- ✅ **5 Ausgabeformate**: Markdown, JSON, HTML, PDF, CSV
- ✅ **4 Prosody-Features**: Tempo, Pitch, Energie, Pausen
- ✅ **7 Emotionale Kategorien**: Automatische Emotionserkennung
- ✅ **Intelligent Pipeline**: Quality-basierte automatische Modellwahl
- ✅ **Speaker Diarization**: Automatische Mehrsprechererkennung
- ✅ **Memory Learning**: Kontinuierliche Verbesserung der Sprecher-Profile
- ✅ **Professional GUI**: One-Click Workflow für Therapeuten

**Status**: Phase 2b Complete ✅
**Nächster Schritt**: ATO-Marker-Integration (Phase 2c)

---

**Dokumentiert**: 2024-06-12
**Version**: 2.0
**Zeilen Code**: 9.767
**Test Coverage**: 12 Test-Suites

**Ready for Therapeutic Applications** 🎯
