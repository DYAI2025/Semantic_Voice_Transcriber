# Speaker Diarization (Phase 2b)

## 🎤 Überblick

Die automatische Sprechererkennung (Speaker Diarization) identifiziert verschiedene Sprecher in einer Audio-Aufnahme und kennzeichnet sie als **Speaker A**, **Speaker B**, **Speaker C**, etc.

**Status:** ✅ Implementiert (Phase 2b)

## 📋 Voraussetzungen

### 1. Hugging Face Account & Token

pyannote.audio erfordert einen kostenlosen Hugging Face Account und Zugriff auf die Modelle:

#### Schritt 1: Account erstellen
- Gehe zu https://huggingface.co/join
- Erstelle einen kostenlosen Account

#### Schritt 2: Modell-Zugriff akzeptieren
Du musst die User Agreements für folgende Modelle akzeptieren:

1. **pyannote/segmentation-3.0**
   - Gehe zu: https://huggingface.co/pyannote/segmentation-3.0
   - Klicke auf "Agree and access repository"

2. **pyannote/speaker-diarization-3.1**
   - Gehe zu: https://huggingface.co/pyannote/speaker-diarization-3.1
   - Klicke auf "Agree and access repository"

#### Schritt 3: Access Token erstellen
- Gehe zu: https://huggingface.co/settings/tokens
- Klicke auf "New token"
- Name: z.B. "SVT_Diarization"
- Type: **Read** (reicht aus)
- Klicke "Generate token"
- **KOPIERE DEN TOKEN!** (Du siehst ihn nur einmal)

Beispiel-Token: `hf_AbCdEfGhIjKlMnOpQrStUvWxYz1234567890`

### 2. Token-Speicherung

Erstelle eine Datei `.env` im Projektverzeichnis:

```bash
# .env
HF_TOKEN=hf_AbCdEfGhIjKlMnOpQrStUvWxYz1234567890
```

**WICHTIG:** Die `.env`-Datei ist bereits in `.gitignore` und wird NICHT ins Repository committed!

## 🚀 Verwendung

### Option 1: Via Python-Code

```python
from auto_transcriber_v4_emotion import transcribe_with_whisper
from pathlib import Path

# Mit Speaker Diarization
result = transcribe_with_whisper(
    audio_path="path/to/audio.m4a",
    model_size='small',
    language='de',
    extract_prosody=True,
    enable_diarization=True,  # ← Aktiviert Sprechererkennung
    hf_token="hf_YOUR_TOKEN_HERE"  # ← Dein HF Token
)

# Segmente enthalten jetzt 'speaker' Feld
for seg in result['segments']:
    print(f"{seg['speaker']}: {seg['text']}")
```

### Option 2: Via GUI (svt.py)

Die GUI wird in einer zukünftigen Version erweitert mit:
- ☐ Checkbox "Sprechererkennung aktivieren"
- ☐ Eingabefeld für HF Token
- ☐ Token aus `.env` automatisch laden

## 📊 Ausgabeformate mit Sprechererkennung

### Markdown (.md)

```markdown
**[00:05 - 00:07] Speaker A:** So, wir haben ja nicht so viel Zeit. `[TEMPO↑]`
  *Tempo: 226.4 WPM (+20.6%) | Tonhöhe: 226.0 Hz (+13.2%)*

**[00:07 - 00:08] Speaker B:** Ja, ich verstehe.
  *Tempo: 180.0 WPM (-4.2%)*

**[00:19 - 00:21] Speaker A:** Lass uns beginnen. `[PAUSE]`
```

### JSON (.prosody.json)

```json
{
  "segments": [
    {
      "index": 0,
      "speaker": "Speaker A",
      "start": 5.26,
      "end": 7.38,
      "text": "So, wir haben ja nicht so viel Zeit.",
      "prosody": { ... }
    }
  ]
}
```

### CSV (.csv)

```csv
index,speaker,start_time,end_time,text,tempo_wpm,...
0,Speaker A,5.26,7.38,"So, wir haben ja nicht so viel Zeit.",226.4,...
1,Speaker B,7.38,8.12,"Ja, ich verstehe.",180.0,...
```

### HTML/PDF

Die Sprecher werden automatisch mit verschiedenen Farben dargestellt:
- **Speaker A:** Blau
- **Speaker B:** Lila
- **Speaker C:** Grün
- **Speaker D:** Orange
- **Speaker E:** Pink
- **Speaker F:** Türkis

## 🎛️ Konfiguration

### Anzahl Sprecher festlegen

```python
# Automatische Erkennung (1-10 Sprecher)
result = transcribe_with_whisper(
    ...,
    enable_diarization=True,
    num_speakers=None  # Auto-detect
)

# Feste Anzahl (z.B. 2 Sprecher)
result = transcribe_with_whisper(
    ...,
    enable_diarization=True,
    num_speakers=2  # Genau 2 Sprecher
)
```

### Speaker-Statistiken

```python
from speaker_diarizer import SpeakerDiarizer

stats = SpeakerDiarizer.get_speaker_statistics(
    result['speaker_segments']
)

for speaker, data in stats.items():
    print(f"{speaker}: {data['total_duration']:.1f}s ({data['percentage']:.1f}%)")
```

Ausgabe:
```
Speaker A: 45.2s (60.3%) - 12 Segmente
Speaker B: 29.8s (39.7%) - 8 Segmente
```

## 🔧 Technische Details

### Verwendete Modelle

- **Segmentation:** pyannote/segmentation-3.0
- **Diarization:** pyannote/speaker-diarization-3.1
- **Embedding:** pyannote/wespeaker-voxceleb-resnet34-LM

### Alignment-Strategie

Die Sprechererkennung läuft **parallel** zur Transkription:

1. **Whisper** transkribiert Audio → Segmente mit Text + Timestamps
2. **pyannote.audio** analysiert Audio → Sprecher-Segmente mit Timestamps
3. **Alignment** ordnet Sprecher den Whisper-Segmenten zu (via Overlap-Berechnung)

### GPU-Beschleunigung

Speaker Diarization verwendet automatisch GPU falls verfügbar:

```python
diarizer = SpeakerDiarizer(
    device='cuda'  # Oder 'cpu' für CPU-only
)
```

## ⚠️ Troubleshooting

### Fehler: "You need to accept user agreement"

```
RuntimeError: You need to accept the conditions to access this repository
```

**Lösung:** Akzeptiere die User Agreements (siehe oben Schritt 2)

### Fehler: "Invalid token"

```
HfHubHTTPError: 401 Client Error: Unauthorized for url
```

**Lösung:**
1. Prüfe ob Token korrekt kopiert wurde (keine Leerzeichen)
2. Erstelle neuen Token mit **Read**-Berechtigung

### Warnung: "Failed to load pipeline"

```
Failed to load pipeline: ...
```

**Mögliche Ursachen:**
- Kein Internetzugang (Modelle werden beim ersten Mal heruntergeladen)
- Token fehlt oder ungültig
- User Agreements nicht akzeptiert

### Langsame Verarbeitung

**Normal:** Diarization dauert ca. 1-2x der Audio-Länge
- 5-Minuten-Audio → 5-10 Minuten Verarbeitung (CPU)
- 5-Minuten-Audio → 1-3 Minuten Verarbeitung (GPU)

**Optimierung:**
- Verwende GPU (CUDA) falls verfügbar
- Reduziere Audio-Qualität vor Verarbeitung (nicht empfohlen für Therapie)

## 📝 Beispiel: Vollständiger Workflow

```python
#!/usr/bin/env python3
from pathlib import Path
from auto_transcriber_v4_emotion import transcribe_with_whisper
from output_formatter import OutputFormatter
import os
from dotenv import load_dotenv  # pip install python-dotenv

# Token aus .env laden
load_dotenv()
HF_TOKEN = os.getenv('HF_TOKEN')

# Audio transkribieren mit Diarization
audio_file = Path("Eingang/Patient/session_2025-01-15.m4a")

result = transcribe_with_whisper(
    audio_path=str(audio_file),
    model_size='small',
    language='de',
    extract_prosody=True,
    enable_diarization=True,
    hf_token=HF_TOKEN,
    num_speakers=2  # Therapeut + Patient
)

# Alle Formate generieren
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

print("✅ Transkription abgeschlossen:")
for format_type, path in files.items():
    if path:
        print(f"  - {format_type.upper()}: {path}")
```

## 🎯 Roadmap

### Phase 2b (Current) ✅
- [x] Automatische Sprechererkennung (Speaker A, B, C)
- [x] Integration in Transkriptionspipeline
- [x] Speaker-Labels in allen Ausgabeformaten
- [x] Farbcodierte Sprecher in HTML/PDF

### Phase 2c (Geplant)
- [ ] GUI-Integration (Checkbox + Token-Feld)
- [ ] Token-Speicherung in Config-Datei
- [ ] Speaker-Namen manuell zuweisen (A → "Therapeut", B → "Patient")
- [ ] Speaker-Embeddings für konsistente Namen über Sessions hinweg

### Phase 3 (Zukunft)
- [ ] Live-Diarization für Streaming-Audio
- [ ] Custom Speaker-Profile (Voice-Print-Datenbank)
- [ ] Multi-Language Speaker Detection

## 📄 Lizenz & Credits

- **pyannote.audio:** MIT License (https://github.com/pyannote/pyannote-audio)
- **Hugging Face:** Community Models mit eigenen Lizenzen
- **SVT:** Proprietär - DYAI 2025

---

**Fragen?** Siehe auch:
- [README.md](README.md) - Allgemeine SVT-Dokumentation
- [Hugging Face Docs](https://huggingface.co/docs/hub/security-tokens)
- [pyannote.audio Docs](https://github.com/pyannote/pyannote-audio)
