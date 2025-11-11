# Semantic Voice Transcriber (SVT)

**Therapeutisches Transkriptionssystem mit Prosodieanalyse für emotionale Wendepunkt-Erkennung**

## 🎯 Überblick

SVT ist ein intelligentes Audio-Transkriptionssystem, das speziell für therapeutische Anwendungen entwickelt wurde. Es kombiniert hochqualitative Spracherkennung (OpenAI Whisper) mit fortgeschrittener Prosodieanalyse, um emotionale Marker in therapeutischen Gesprächen zu erkennen und zu markieren.

## ✨ Hauptfunktionen

### Phase 1: Prosodieextraktion (✅ Abgeschlossen)

- **🎵 Prosodische Merkmale ("Big 4")**
  - **Tempo**: Wörter pro Minute (WPM) mit Abweichungserkennung
  - **Tonhöhe (Pitch)**: F0-Analyse in Hz mit Parselmouth/Praat
  - **Energie**: RMS und dB-Werte
  - **Pausen**: Automatische Pausenerkennung (>1s)

- **📊 Baseline-Berechnung**
  - Globale Baseline pro Audio-Datei
  - Prozentuale Abweichungserkennung
  - Adaptive Marker-Trigger

- **📝 Ausgabeformate**
  - **Annotiertes Markdown**: Für Therapeuten lesbar mit inline Markern
  - **JSON Sidecar**: Strukturierte Daten für Systemverarbeitung

### Beispiel-Ausgabe

\`\`\`markdown
**[00:05 - 00:07]** So, wir haben ja nicht so viel Zeit. \`[TEMPO↑]\`
  *Tempo: 226.4 WPM (+20.6%) | Tonhöhe: 226.0 Hz (+13.2%) | Energie: 0.0836 (+5.5%)*

**[00:07 - 00:08]** Wolli, wir müssen sprechen. \`[TEMPO↑]\`
  *Tempo: 272.7 WPM (+45.3%) | Tonhöhe: 211.2 Hz (+5.8%)*

**[00:19 - 00:21]** Wolli, we need to talk. \`[PITCH↓]\` \`[ENERGY↓]\` \`[PAUSE]\`
  *Tempo: 182.9 WPM (-2.5%) | Tonhöhe: 168.7 Hz (-15.5%) | Energie: 0.0497 (-37.3%)*
\`\`\`

### Marker-Schwellwerte

- \`[TEMPO↑/↓]\`: ±20% Abweichung von Baseline
- \`[PITCH↑/↓]\`: ±15% Abweichung von Baseline
- \`[ENERGY↑/↓]\`: ±25% Abweichung von Baseline
- \`[PAUSE]\`: Pause >1000ms

## 🚀 Installation

### Voraussetzungen

\`\`\`bash
# Python 3.12+
sudo apt install python3.12 python3-pip

# System-Abhängigkeiten
sudo apt install ffmpeg portaudio19-dev
\`\`\`

### Python-Pakete

\`\`\`bash
pip install --break-system-packages openai-whisper librosa praat-parselmouth \\
    soundfile pyyaml numpy textblob nltk
\`\`\`

### TextBlob Setup (lokal)

\`\`\`bash
# Bereits im Repo enthalten unter TextBlob/
# NLTK Daten werden beim ersten Start automatisch heruntergeladen
\`\`\`

## 📖 Verwendung

### GUI starten

\`\`\`bash
python3 svt.py
\`\`\`

### Hauptfunktionen in der GUI

1. **🚀 Transkription starten**
   - Wähle Audio-Dateien aus (m4a, opus, wav, mp3)
   - Aktiviere gewünschte Features (Emotions-Analyse, Prosody, Memory)
   - Starte Batch-Transkription

2. **🧪 Quick Test**
   - Testet erste Audio-Datei komplett
   - Zeigt Qualitätsanalyse und Transkript

3. **🎵 Prosody Test (30s)**
   - Extrahiert erste 30 Sekunden
   - Vollständige Prosodieanalyse
   - Generiert annotiertes Markdown + JSON

### Features

- ✅ **Intelligent Pipeline**: Automatische Qualitätsanalyse und Modellwahl
- ✅ **Prosody-Extraktion**: Voice-Marker 2.0 mit Big 4 Features
- ✅ **Emotions-Analyse**: TextBlob Sentiment + Marker-System
- ✅ **Speaker Diarization**: Automatische Sprechererkennung (Speaker A, B, C)
- ✅ **Multi-Format Export**: Markdown, JSON, HTML, PDF, CSV
- ✅ **Professional Layout**: Farbcodierte Sprecher und emotionale Wendepunkte

## 📁 Projektstruktur

\`\`\`
Semantic_Voice_Transcriber/
├── svt.py                          # Haupt-GUI
├── auto_transcriber_v4_emotion.py  # Transkription + Emotion
├── prosody_extractor.py            # Prosodieextraktion (Phase 1)
├── output_formatter.py             # Markdown + JSON Formatter
├── audio_quality_analyzer.py       # Qualitätsanalyse
├── audio_preprocessor.py           # Audio-Vorverarbeitung
├── test_prosody_pipeline.py        # Pipeline-Test
├── Eingang/                        # Audio-Eingabe
│   └── Patient/                    # Unterordner für Sprecher
├── Transkripte_LLM/                # Transkript-Ausgabe
│   ├── *.md                        # Annotierte Markdown
│   └── *.prosody.json              # JSON Sidecar
├── Memory/                         # Sprecher-Profile
├── VP_ATO/                         # Atomic Voice Markers
├── Marker_LD3.5_SSoTh/             # 4-Tier Marker-System
└── TextBlob/                       # Lokales TextBlob
\`\`\`

## 🎯 Roadmap

### Phase 2a: Professional Layout & Export (✅ Abgeschlossen)

- [x] HTML-Export mit farbcodierten Sprechern
- [x] PDF-Export via WeasyPrint
- [x] CSV-Export für Datenanalyse
- [x] Emotionale Wendepunkt-Hervorhebung (orange)
- [x] Farbige Prosody-Marker in allen Formaten

### Phase 2b: Speaker Diarization (✅ Abgeschlossen)

- [x] Automatische Sprechererkennung mit pyannote.audio
- [x] Speaker A, B, C Labels ohne Namenszuordnung
- [x] Integration in Transkriptionspipeline
- [x] Speaker-Labels in allen Ausgabeformaten (MD, JSON, HTML, PDF, CSV)
- [x] Farbcodierte Sprecher in HTML/PDF (6 Farben)

**Siehe:** [SPEAKER_DIARIZATION.md](SPEAKER_DIARIZATION.md) für Details & HF Token Setup

### Phase 2c: Overlapped Speech Detection (✅ Abgeschlossen)

- [x] Automatische Erkennung überlappender Sprache mit pyannote.audio
- [x] OSD-Marker in allen Ausgabeformaten (`[ÜBERLAPPUNG Xs]`)
- [x] Visualisierung in HTML/PDF (pink border + badge)
- [x] Segment-Flagging (has_overlap, overlap_duration)
- [x] Therapeutische Anwendungen (Interruptions-Analyse, Turn-Taking Dynamik)

**Siehe:** [docs/OSD_GUIDE.md](docs/OSD_GUIDE.md) für Details & therapeutische Anwendungen

### Phase 2d: ATO-Marker-Integration (In Planung)

- [ ] VP_ATO/*.yaml Marker mit Prosodieabweichungen verknüpfen
- [ ] Echtzeit-Marker-Trigger beim Transkribieren
- [ ] ATO → SEM → CLU → MEMA Hierarchie aufbauen
- [ ] Wendepunkt-Erkennung für Therapeuten
- [ ] GUI-Integration für Speaker Diarization & OSD

### Phase 3: Streaming & Real-Time

- [ ] Live-Transkription mit Prosody
- [ ] Echtzeit-Marker-Anzeige
- [ ] WebSocket-Interface für externe Tools

## 🔧 Technische Details

### Whisper-Modelle

- **tiny**: 39M Parameter, schnell, weniger genau
- **base**: 74M Parameter, guter Kompromiss
- **small**: 244M Parameter (Standard für Tests)
- **medium**: 769M Parameter, sehr genau
- **large**: 1550M Parameter, beste Qualität

### Prosodieextraktion

- **Parselmouth**: Praat-basierte Tonhöhenextraktion mit Jitter/Shimmer
- **Librosa**: Audio-Feature-Extraktion (Energie, Tempo)
- **Segmentierung**: Whisper-Segmente (3-10s, semantisch sinnvoll)
- **Baseline**: Globaler Mittelwert pro Audio-Datei

## 🤝 Mitarbeit

Dieses Projekt wurde entwickelt für therapeutische Anwendungen mit Fokus auf:
- Emotionale Wendepunkt-Erkennung
- Prosodiebasierte Marker-Systeme
- DYAI-Framework Integration (LD3.x, ATO/SEM/CLU/MEMA)

## 📄 Lizenz

Proprietär - DYAI 2025

## 🙏 Credits

- **OpenAI Whisper**: Speech-to-Text
- **Parselmouth**: Praat Python Interface
- **Librosa**: Audio Analysis
- **TextBlob**: Sentiment Analysis
- **Claude Code**: Development Assistant

---

**Status**: Phase 2c Complete ✅
**Nächster Schritt**: GUI-Integration & ATO-Marker-Integration (Phase 2d)
