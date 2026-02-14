# SVT Projekt Plan - 2026-02-14

## Vision
**"Transkription der Welt für Therapeuten"**

## Features nach Priorität

### Phase 1: MVP - Transkription Core (1-2 Wochen)
- [ ] Whisper Transcription (max 4h Audio)
- [ ] Speaker Diarization (pyannote.audio)
- [ ] CLI Interface (`python transcribe.py audio.mp3`)
- [ ] Output: JSON + Text

### Phase 2: Intelligence (2-3 Wochen)
- [ ] Claude/Gemini Summary
- [ ] ATO Marker Integration
- [ ] Prosody Analysis
- [ ] Therapeutische Vorschläge

### Phase 3: Output & Performance (1-2 Wochen)
- [ ] PDF Export (professional formatting)
- [ ] DOCX Export
- [ ] Semi-parallel Transcription
- [ ] 99,99% Speaker Confidence

### Phase 4: Deployment (1 Woche)
- [ ] Deutscher Server (Hetzner/IONOS)
- [ ] DSGVO Compliance
- [ ] Web Interface (optional)

## Aktueller Stand

### Funktioniert bereits:
- ✅ Whisper Integration
- ✅ Speaker Separation
- ✅ Super Semantic Processor
- ✅ ATO Marker System
- ✅ Prosody Analyzer
- ✅ Multiple Output Formats

### Fehlt noch:
- [ ] Semi-parallel Transcription
- [ ] High-confidence Speaker Model
- [ ] Deutsche Server Konfiguration
- [ ] Production Web Interface

## Dependencies

| Was | Status |
|-----|--------|
| openai-whisper | ✅ |
| pyannote.audio | ✅ |
| torch | ✅ |
| librosa | ✅ |
| Claude API | ⚠️ Key fehlt |
| Gemini API | ⚠️ Key fehlt |

## Setup

```bash
# Installieren
cd /home/moltbot/Semantic_Voice_Transcriber
pip install -r requirements.txt

# Transkribieren
python transcribe_mvp.py audio.mp3

# Output in ./transcripts/
```

## Nächste Schritte

1. **MVP Testen** - Funktioniert der aktuelle Code?
2. **Lücken identifizieren** - Was genau fehlt?
3. **Priorisieren** - Was zuerst bauen?

## Timeline Schätzung

| Phase | Zeit |
|-------|------|
| Phase 1 (Core) | 1-2 Wochen |
| Phase 2 (Intelligence) | 2-3 Wochen |
| Phase 3 (Output) | 1-2 Wochen |
| Phase 4 (Deployment) | 1 Woche |

**Total: 5-8 Wochen für Complete Version**
