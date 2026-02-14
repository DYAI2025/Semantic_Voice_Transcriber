# SVT Local - Anforderungen

## Für Therapeuten (einfache Installation)

### Windows Installation (1-Click)

```bash
# Python installieren (von python.org)
# Dann dieses Script ausführen:

pip install pysimplegui openai-whisper torch pyannote.audio \
    librosa ffmpeg-python python-docx reportlab

# Starten
python svt_local_gui.py
```

### Oder mit pip install (kommend)

```bash
pip install svt-local
svt-local
```

## Dependencies (automatisch)

| Package | Version | Beschreibung |
|---------|---------|-------------|
| PySimpleGUI | >=4.60 | Einfache GUI |
| openai-whisper | latest | Transcription |
| torch | latest | ML Framework |
| pyannote.audio | latest | Speaker Diarization |
| librosa | latest | Audio Analysis |
| ffmpeg-python | latest | Audio Processing |
| python-docx | latest | DOCX Export |
| reportlab | latest | PDF Export |

## System Anforderungen

- **Windows 10/11** (64-bit)
- **Python 3.10+**
- **RAM:** 8GB minimum (16GB empfohlen)
- **Speicher:** 5GB für Modelle
- **CPU:** Intel/AMD (CUDA GPU optional für Speed)

## Installation Schritte

1. Python 3.10 von python.org herunterladen
2. Installieren (✓ "Add to PATH" aktivieren)
3. Command Prompt öffnen
4. `pip install pysimplegui openai-whisper torch` ausführen
5. SVT Local starten: `python svt_local_gui.py`

## Troubleshooting

**FFmpeg nicht gefunden:**
```
pip install ffmpeg-python
```

**CUDA/GPU Support (optional):**
```
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

**RAM Probleme:**
- Kleinere Whisper Modelle nutzen (`-m small` statt `-m medium`)
