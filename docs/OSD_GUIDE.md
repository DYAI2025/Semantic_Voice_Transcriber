# Overlapped Speech Detection (OSD) Guide

## 🎯 Überblick

Overlapped Speech Detection (OSD) identifiziert Momente, in denen mehrere Sprecher gleichzeitig sprechen. Dies ist entscheidend für therapeutische Transkripte, um Unterbrechungen, simultane Sprache und Gesprächsdynamik zu markieren.

**Status:** ✅ Implementiert (Phase 2c)

## 🚀 Verwendung

### Python API

```python
from auto_transcriber_v4_emotion import transcribe_with_whisper
import os

result = transcribe_with_whisper(
    audio_path="session.m4a",
    model_size='small',
    language='de',
    enable_overlap_detection=True,  # OSD aktivieren
    osd_min_duration=0.5,  # Überlappungen < 0.5s ignorieren
    hf_token=os.getenv('HF_TOKEN')
)

# Zugriff auf Überlappungsbereiche
for overlap in result['overlapped_speech']:
    print(f"Überlappung: {overlap['start']:.2f}s - {overlap['end']:.2f}s")
    print(f"  Dauer: {overlap['duration']:.2f}s")

# Segmente auf Überlappungen prüfen
for seg in result['segments']:
    if seg.get('has_overlap'):
        print(f"Segment {seg['index']} hat {seg['overlap_duration']:.1f}s Überlappung")
        print(f"  Text: {seg['text']}")
```

### Kombiniert mit Speaker Diarization

```python
# Beste Ergebnisse: OSD + Diarization zusammen
result = transcribe_with_whisper(
    audio_path="session.m4a",
    model_size='small',
    extract_prosody=True,           # Prosody-Marker
    enable_diarization=True,        # Sprecher A, B, C
    enable_overlap_detection=True,  # Überlappungen
    hf_token=os.getenv('HF_TOKEN')
)

# Zeigt: Welcher Sprecher unterbricht wen?
for seg in result['segments']:
    if seg.get('has_overlap'):
        print(f"{seg['speaker']}: {seg['text']} [ÜBERLAPPUNG {seg['overlap_duration']:.1f}s]")
```

## 📊 Ausgabeformate

### Markdown (.md)

```markdown
**[00:12 - 00:15] Speaker A:** Ich denke dass wir heute... `[ÜBERLAPPUNG 1.2s]`
  *Tempo: 180 WPM | Tonhöhe: 210 Hz*

**[00:13 - 00:16] Speaker B:** Moment, lass mich ausreden! `[ÜBERLAPPUNG 1.0s]` `[PITCH↑]`
  *Tempo: 240 WPM (+33%) | Tonhöhe: 280 Hz (+18%)*
```

**Marker-Bedeutung:**
- `[ÜBERLAPPUNG Xs]` = Segment enthält X Sekunden simultane Sprache

### JSON (.prosody.json)

```json
{
  "segments": [
    {
      "index": 0,
      "speaker": "Speaker A",
      "start": 12.0,
      "end": 15.0,
      "text": "Ich denke dass wir heute...",
      "has_overlap": true,
      "overlap_duration": 1.2,
      "prosody": { ... }
    }
  ],
  "overlapped_speech": [
    {
      "start": 13.0,
      "end": 14.2,
      "duration": 1.2,
      "overlap_type": "simultaneous_speech"
    }
  ]
}
```

### CSV (.csv)

```csv
index,speaker,start_time,end_time,text,has_overlap,overlap_duration_s,tempo_wpm,...
0,Speaker A,12.0,15.0,"Ich denke dass...",True,1.2,180,...
1,Speaker B,13.0,16.0,"Moment, lass mich...",True,1.0,240,...
```

### HTML/PDF

Überlappungen werden visuell hervorgehoben:
- **Pink/Magenta Rahmen**: 4px solid #E91E63
- **Gradient-Hintergrund**: Leichter rosa Verlauf
- **Überlappungs-Badge**: "⚠ Überlappung 1.2s" im Segment-Header

![OSD HTML Example](../assets/osd_example.png)

## 🎛️ Parameter

### enable_overlap_detection
- **Typ:** `bool`
- **Default:** `False`
- **Beschreibung:** Aktiviert/deaktiviert OSD
- **Beispiel:**
  ```python
  result = transcribe_with_whisper(..., enable_overlap_detection=True)
  ```

### osd_min_duration
- **Typ:** `float`
- **Default:** `0.5` (Sekunden)
- **Beschreibung:** Minimale Dauer für Überlappungserkennung
- **Empfehlung:**
  - `0.3s` - Sehr sensitiv (erfasst auch kurze Unterbrechungen)
  - `0.5s` - Standard (gute Balance)
  - `1.0s` - Nur längere Überlappungen
- **Beispiel:**
  ```python
  result = transcribe_with_whisper(
      ...,
      enable_overlap_detection=True,
      osd_min_duration=0.3  # Sehr sensitiv
  )
  ```

### hf_token
- **Typ:** `str`
- **Erforderlich:** Ja (für OSD und Diarization)
- **Beschreibung:** Hugging Face Access Token
- **Siehe:** [SPEAKER_DIARIZATION.md](../SPEAKER_DIARIZATION.md#1-hugging-face-account--token) für Token-Setup

## 🩺 Therapeutische Anwendungen

### 1. Unterbrechungsanalyse

Wer unterbricht wen? Wie oft?

```python
# Analysiere Unterbrechungsmuster
interruptions = {}
for seg in result['segments']:
    if seg.get('has_overlap'):
        speaker = seg['speaker']
        interruptions[speaker] = interruptions.get(speaker, 0) + 1

print("Unterbrechungen pro Sprecher:")
for speaker, count in sorted(interruptions.items()):
    print(f"  {speaker}: {count}x")
```

**Therapeutischer Wert:**
- Dominanzverhalten erkennen
- Gesprächs-Asymmetrie quantifizieren
- Veränderungen über Therapieverlauf tracken

### 2. Turn-Taking Dynamik

Wie fließend ist das Gespräch?

```python
# Berechne Overlap-Rate
total_duration = result['segments'][-1]['end']
overlap_duration = sum(o['duration'] for o in result['overlapped_speech'])
overlap_rate = (overlap_duration / total_duration) * 100

print(f"Überlappungsrate: {overlap_rate:.1f}%")
```

**Interpretation:**
- `< 5%` - Sehr strukturiert, möglicherweise zu formal
- `5-15%` - Natürlicher Gesprächsfluss
- `> 15%` - Häufige Unterbrechungen, möglicherweise Konflikt

### 3. Engagement-Metriken

Identifiziere emotional engagierte vs. passive Momente

```python
# Kombiniere OSD + Prosody-Marker
for seg in result['segments']:
    if seg.get('has_overlap') and 'TEMPO↑' in seg.get('markers', []):
        print(f"Hoch-Engagement-Moment bei {seg['start']:.1f}s:")
        print(f"  {seg['speaker']}: {seg['text']}")
```

**Therapeutischer Wert:**
- Identifiziere Themen mit hoher emotionaler Beteiligung
- Erkenne Momente der Co-Konstruktion
- Tracke Engagement-Level über Zeit

### 4. Konflikt-Erkennung

Überlappungen können Spannung indizieren

```python
# Finde "Konflikt-Cluster" (mehrere Overlaps in kurzer Zeit)
overlap_times = [o['start'] for o in result['overlapped_speech']]
for i in range(len(overlap_times) - 2):
    if overlap_times[i+2] - overlap_times[i] < 30:  # 3 Overlaps in 30s
        print(f"⚠ Konflikt-Cluster bei {overlap_times[i]:.1f}s")
```

## 🔧 Technische Details

### Verwendete Modelle

- **Modell:** `pyannote/segmentation-3.0`
- **Pipeline:** `MultiLabelSegmentation` mit Powerset-Encoding
- **Framework:** pyannote.audio 4.0
- **Embedding:** Inkludiert im Segmentation-Modell

### Powerset-Encoding

Das segmentation-3.0 Modell verwendet Powerset-Encoding für Multi-Label-Ausgabe:

- `SPEAKER_00` - Nur Sprecher 0 spricht
- `SPEAKER_01` - Nur Sprecher 1 spricht
- `SPEAKER_00+SPEAKER_01` - **Beide sprechen gleichzeitig** ⚠

SVT erkennt Überlappungen durch das `+` Zeichen in Labels.

### Verarbeitungsablauf

```
Audio-Datei
    │
    ├──> Whisper Transkription
    │      └──> Segmente mit Text + Timestamps
    │
    ├──> pyannote Speaker Diarization (optional)
    │      └──> Sprecher-Labels (A, B, C)
    │
    ├──> pyannote OSD (wenn aktiviert)
    │      └──> Überlappungsbereiche
    │
    └──> Alignment & Marking
           └──> Segmente mit has_overlap + overlap_duration
```

### Performance

- **Verarbeitungszeit:** +20-30% zu normaler Transkription
- **GPU-Beschleunigung:** Ja (via PyTorch)
- **Parallelisierung:** OSD läuft parallel zu Diarization
- **Memory:** ~2-3 GB zusätzlich für Segmentation-Modell

### Installation

```bash
# Voraussetzungen (bereits installiert wenn Diarization funktioniert)
pip install pyannote.audio torch torchaudio

# Modell-Zugriff
# 1. HF Account erstellen: https://huggingface.co/join
# 2. Akzeptiere: https://huggingface.co/pyannote/segmentation-3.0
# 3. Token erstellen: https://huggingface.co/settings/tokens
```

## ⚠️ Troubleshooting

### Zu viele False Positives

**Problem:** OSD erkennt Überlappungen wo keine sind

**Lösungen:**
1. Erhöhe `osd_min_duration`:
   ```python
   osd_min_duration=1.0  # Nur längere Overlaps
   ```
2. Prüfe Audio-Qualität (zu viel Hintergrundgeräusch?)
3. Verwende Audio-Preprocessing (siehe `audio_preprocessor.py`)

### Fehlende Überlappungen

**Problem:** OSD erkennt bekannte Überlappungen nicht

**Lösungen:**
1. Reduziere `osd_min_duration`:
   ```python
   osd_min_duration=0.2  # Sehr sensitiv
   ```
2. Prüfe ob Audio zu leise ist
3. Erhöhe Audio-Qualität vor Verarbeitung

### "Failed to load OSD pipeline"

**Problem:**
```
Failed to load OSD pipeline: You need to accept user conditions
```

**Lösung:**
1. Gehe zu: https://huggingface.co/pyannote/segmentation-3.0
2. Klicke "Agree and access repository"
3. Warte 1-2 Minuten (Propagation)
4. Versuche erneut

### Token-Fehler

**Problem:**
```
HfHubHTTPError: 401 Client Error: Unauthorized
```

**Lösung:**
```bash
# Prüfe Token
echo $HF_TOKEN

# Neu laden
export HF_TOKEN=hf_YOUR_TOKEN_HERE

# Oder via .env
echo "HF_TOKEN=hf_YOUR_TOKEN_HERE" > .env
```

### Keine GPU-Beschleunigung

**Problem:** OSD läuft langsam (nur CPU)

**Check:**
```python
import torch
print(f"CUDA available: {torch.cuda.is_available()}")
```

**Lösung:**
- Installiere CUDA-kompatibles PyTorch
- Siehe: https://pytorch.org/get-started/locally/

## 📝 Beispiel: Vollständiger Workflow

```python
#!/usr/bin/env python3
from pathlib import Path
from auto_transcriber_v4_emotion import transcribe_with_whisper
from output_formatter import OutputFormatter
from speaker_diarizer import SpeakerDiarizer
import os
from dotenv import load_dotenv

# Token laden
load_dotenv()
HF_TOKEN = os.getenv('HF_TOKEN')

# Audio transkribieren mit OSD + Diarization
audio_file = Path("Eingang/Patient/session_2025-01-15.m4a")

result = transcribe_with_whisper(
    audio_path=str(audio_file),
    model_size='small',
    language='de',
    extract_prosody=True,
    enable_diarization=True,        # Sprecher erkennen
    enable_overlap_detection=True,  # Überlappungen erkennen
    osd_min_duration=0.5,
    hf_token=HF_TOKEN,
    num_speakers=2  # Therapeut + Patient
)

# Statistiken ausgeben
print(f"\n📊 Transkriptions-Statistik:")
print(f"  Segmente: {len(result['segments'])}")
print(f"  Sprecher: {len(set(s['speaker'] for s in result['segments']))}")
print(f"  Überlappungen: {len(result['overlapped_speech'])}")

overlaps_with_duration = [s for s in result['segments'] if s.get('has_overlap')]
print(f"  Segmente mit Overlap: {len(overlaps_with_duration)}")

# Ausgabeformate generieren
formatter = OutputFormatter()
output_base = Path("Transkripte_LLM") / audio_file.stem

files = formatter.format_all(
    transcription_result=result,
    audio_filename=audio_file.name,
    output_path=output_base,
    generate_html=True,
    generate_pdf=True,
    generate_csv=True
)

print("\n✅ Transkription abgeschlossen:")
for format_type, path in files.items():
    if path:
        print(f"  - {format_type.upper()}: {path}")

# Therapeutische Analyse
print("\n🩺 Therapeutische Insights:")

# 1. Unterbrechungsmuster
interruptions = {}
for seg in result['segments']:
    if seg.get('has_overlap'):
        speaker = seg['speaker']
        interruptions[speaker] = interruptions.get(speaker, 0) + 1

if interruptions:
    print("\n  Unterbrechungen:")
    for speaker, count in sorted(interruptions.items()):
        print(f"    {speaker}: {count}x")

# 2. Overlap-Rate
total_duration = result['segments'][-1]['end'] if result['segments'] else 0
overlap_duration = sum(o['duration'] for o in result['overlapped_speech'])
if total_duration > 0:
    overlap_rate = (overlap_duration / total_duration) * 100
    print(f"\n  Überlappungsrate: {overlap_rate:.1f}%")

# 3. Konflikt-Cluster
overlap_times = sorted([o['start'] for o in result['overlapped_speech']])
clusters = []
for i in range(len(overlap_times) - 2):
    if overlap_times[i+2] - overlap_times[i] < 30:
        clusters.append(overlap_times[i])

if clusters:
    print(f"\n  ⚠ {len(clusters)} Konflikt-Cluster erkannt bei:")
    for time in clusters[:3]:  # Top 3
        print(f"    {time:.1f}s")
```

## 🎯 Best Practices

### 1. Kombiniere OSD mit anderen Features

```python
# EMPFOHLEN: Alle Features zusammen
result = transcribe_with_whisper(
    audio_path=audio,
    extract_prosody=True,           # Emotionale Marker
    enable_diarization=True,        # Sprecher
    enable_overlap_detection=True,  # Überlappungen
    hf_token=token
)
```

**Warum:** OSD allein zeigt nur WO Überlappungen sind. Mit Prosody + Diarization siehst du WER WIE überlappen (emotional, schnell, laut).

### 2. Tune osd_min_duration für deinen Use-Case

```python
# Therapie-Gespräch (strukturiert)
osd_min_duration=0.5  # Standard

# Familiengespräch (lebhaft)
osd_min_duration=0.3  # Sensitiver

# Konfliktsituation (chaotisch)
osd_min_duration=0.8  # Nur bedeutende Overlaps
```

### 3. Verwende CSV für Langzeit-Analyse

```python
import pandas as pd

# CSV laden
df = pd.read_csv('Transkripte_LLM/session.csv')

# Analyse
overlap_segments = df[df['has_overlap'] == True]
print(f"Overlap-Rate: {len(overlap_segments) / len(df) * 100:.1f}%")

# Pro Sprecher
overlap_by_speaker = overlap_segments.groupby('speaker').size()
print(overlap_by_speaker)
```

## 🔗 Siehe Auch

- [SPEAKER_DIARIZATION.md](../SPEAKER_DIARIZATION.md) - Speaker Diarization Setup
- [README.md](../README.md) - Allgemeine SVT-Dokumentation
- [pyannote.audio Docs](https://github.com/pyannote/pyannote-audio) - Upstream-Dokumentation
- [Hugging Face Segmentation-3.0](https://huggingface.co/pyannote/segmentation-3.0) - Modell-Details

## 📄 Lizenz & Credits

- **pyannote.audio:** MIT License
- **segmentation-3.0:** MIT License (siehe HF Model Card)
- **SVT:** Proprietär - DYAI 2025

---

**Status:** Phase 2c Complete ✅
**Entwickelt mit:** Claude Code
