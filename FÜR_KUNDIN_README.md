# SVT - Semantic Voice Transcriber
## Professionelles Transkriptionssystem für therapeutische Sitzungen

---

## 🎯 **SCHNELLSTART**

### 1. **Audio-Datei platzieren**
```
Eingang/
  └── Patient/
      └── ihre_audio_datei.m4a
```

### 2. **SVT GUI starten**
```bash
python3 svt.py
```

### 3. **In der GUI:**
- Audiodatei auswählen
- Features aktivieren:
  - ✅ Prosody Analysis (Sprachmelodie, Tempo, Energie)
  - ✅ Speaker Diarization (Sprechertrennung)
  - ✅ Emotion Analysis (Emotionserkennung)
- "Transkription starten" klicken

### 4. **Ergebnisse finden**
```
Transkripte_LLM/
  ├── transkript.html    ← **HAUPTDATEI** (im Browser öffnen)
  ├── transkript.pdf     ← PDF-Version
  ├── transkript.md      ← Markdown mit Markern
  └── transkript.prosody.json  ← Strukturierte Daten
```

---

## ✨ **KERNFUNKTIONEN**

### ✅ **Sprechertrennung** (Speaker Diarization)
- Automatische Erkennung mehrerer Sprecher
- Labels: Speaker A, B, C...
- Überlappungen werden erkannt: `[ÜBERLAPPUNG 2.3s]`

### ✅ **Hochgenaue Spracherkennung**
- Whisper AI (OpenAI)
- Deutsche Sprachoptimierung
- Modellgrößen: small, medium, large
- Automatische Qualitätserkennung

### ✅ **Prosody-Analyse** (Sprachmelodie)
Erkennt automatisch:
- `[TEMPO↑]` / `[TEMPO↓]` - Geschwindigkeitsänderungen
- `[PITCH↑]` / `[PITCH↓]` - Tonhöhenänderungen
- `[ENERGY↑]` / `[ENERGY↓]` - Lautstärkeänderungen
- `[PAUSE]` - Signifikante Pausen (>1s)

### ✅ **Turning Points** (Wendepunkte)
Markierung therapeutisch relevanter Momente:
- Emotionale Veränderungen
- Thematische Wechsel
- Kognitive Umstrukturierung
- Einsichtsmomente

### ✅ **Patientenzustand-Marker**
Semantische Analyse für:
- Emotionaler Zustand (Valenz, Aktivierung, Dominanz)
- Kognitive Muster (Metakognition, Reflexion)
- Therapeutische Marker (MEMA, ATO, etc.)

### ✅ **HTML-Output**
Professionelle Darstellung mit:
- Farbcodierte Sprecher
- Zeitstempel
- Prosody-Verläufe als Grafiken
- Turning Points hervorgehoben
- Druckoptimiert (PDF-Export)

---

## 📊 **OUTPUT-FORMATE**

### 1. **HTML** (Hauptformat für Therapeuten)
- Öffnen im Browser: Firefox, Chrome, Safari
- Drucken → PDF speichern
- Alle Features visuell dargestellt
- **Empfohlenes Format für Review**

### 2. **PDF** (Automatisch generiert)
- Direkter PDF-Export
- Identisch mit HTML-Ansicht
- Archivierung und Weitergabe

### 3. **Markdown** (Editierbar)
- Textformat mit Markern
- In jedem Editor öffnen
- Manuelle Nachbearbeitung möglich

### 4. **JSON** (Maschinell lesbar)
- Strukturierte Prosody-Daten
- Für weitere Datenverarbeitung
- API-Integration möglich

---

## ⚙️ **SYSTEMANFORDERUNGEN**

### Betriebssysteme
- ✅ Linux (Ubuntu 20.04+)
- ✅ macOS (Big Sur+)
- ✅ Windows 10/11

### Hardware
- **CPU**: 4+ Kerne (empfohlen 8+)
- **RAM**: 8 GB minimum (16 GB empfohlen)
- **GPU**: Optional (CUDA für schnellere Verarbeitung)
- **Speicher**: 10 GB frei

### Software
- Python 3.10+
- FFmpeg (Audio-Konvertierung)

---

## 🔧 **INSTALLATION**

### Schritt 1: Repository klonen
```bash
git clone <repository-url>
cd Super_semantic_whisper
```

### Schritt 2: Dependencies installieren
```bash
pip install -r requirements.txt
pip install -r requirements_emotion.txt
```

### Schritt 3: Sprachmodelle installieren
```bash
# spaCy Deutsch
python -m spacy download de_core_news_sm

# Whisper-Modelle werden automatisch heruntergeladen
```

### Schritt 4: Hugging Face Token (für Speaker Diarization)
Siehe `SPEAKER_DIARIZATION.md` für Details:
1. Account bei https://huggingface.co/ erstellen
2. Token erstellen
3. `.env` Datei mit Token erstellen

---

## 🎓 **VERWENDUNG**

### GUI-Modus (Empfohlen)
```bash
python3 svt.py
```

### Command-Line Modus
```bash
python3 auto_transcriber_v4_emotion.py \
  --audio Eingang/Patient/session.m4a \
  --model medium \
  --speaker-diarization \
  --prosody
```

### Quick Test
```bash
python3 QUICK_TEST_FOR_CUSTOMER.py
```
Prüft alle Features und generiert Test-Output.

---

## 📁 **VERZEICHNISSTRUKTUR**

```
Super_semantic_whisper/
├── svt.py                      # GUI-Anwendung
├── auto_transcriber_v4_emotion.py  # Hauptmodul
├── prosody_extractor.py        # Prosody-Analyse
├── speaker_diarizer.py         # Sprechertrennung
├── output_formatter.py         # Output-Generierung
├── html_formatter.py           # HTML/PDF-Export
│
├── Eingang/                    # INPUT: Audio-Dateien
│   └── Patient/                # Sprecherspezifische Ordner
│
├── Transkripte_LLM/            # OUTPUT: Alle Ergebnisse
│   ├── *.html                  # HTML-Transkripte
│   ├── *.pdf                   # PDF-Versionen
│   ├── *.md                    # Markdown-Transkripte
│   └── *.prosody.json          # Prosody-Daten
│
└── Memory/                     # Sprecher-Profile
    └── *.yaml                  # Persistente Profile
```

---

## 🐛 **PROBLEMLÖSUNG**

### Problem: "ModuleNotFoundError: No module named 'whisper'"
```bash
pip install openai-whisper
```

### Problem: "OSError: [E050] Can't find model 'de_core_news_sm'"
```bash
python -m spacy download de_core_news_sm
```

### Problem: Speaker Diarization funktioniert nicht
1. `.env` Datei mit Hugging Face Token erstellen
2. pyannote.audio installieren: `pip install pyannote.audio`
3. Modell-Agreements akzeptieren (siehe `SPEAKER_DIARIZATION.md`)

### Problem: HTML-Output fehlt
```bash
pip install weasyprint
# macOS: brew install weasyprint
# Ubuntu: sudo apt-get install weasyprint
```

---

## 📞 **SUPPORT**

### Dokumentation
- **Hauptdokumentation**: `README.md`
- **Speaker Diarization**: `SPEAKER_DIARIZATION.md`
- **Claude AI Guidance**: `CLAUDE.md`

### Logs
- Hauptlog: `transcription_v4_emotion.log`
- GUI-Log: Im Terminal-Output

### Kontakt
Bei Fragen oder Problemen:
- Issues auf GitHub erstellen
- Log-Dateien mitsenden
- Screenshots bei GUI-Problemen

---

## ✅ **CHECKLISTE VOR NUTZUNG**

- [ ] Python 3.10+ installiert
- [ ] FFmpeg installiert (`ffmpeg -version`)
- [ ] Dependencies installiert (`pip install -r requirements.txt`)
- [ ] spaCy-Modell installiert (`python -m spacy list`)
- [ ] Hugging Face Token konfiguriert (`.env`)
- [ ] Test durchgeführt (`python3 QUICK_TEST_FOR_CUSTOMER.py`)
- [ ] Beispiel-Audio transkribiert
- [ ] HTML-Output im Browser geöffnet

---

## 🚀 **PRODUKTIVBETRIEB**

### Beste Praxis
1. **Audio-Qualität**: Mindestens 16kHz, mono oder stereo
2. **Dateilänge**: Optimal 5-60 Minuten (längere Dateien aufteilen)
3. **Whisper-Modell**:
   - `small`: Schnell, gute Qualität (Empfohlen für Tests)
   - `medium`: Balance (Empfohlen für Produktion)
   - `large`: Höchste Qualität (langsam)
4. **Speaker Diarization**: Immer aktivieren für Therapiesitzungen
5. **Prosody Analysis**: Immer aktivieren für vollständige Analyse

### Performance-Tipps
- GPU-Beschleunigung nutzen (CUDA)
- Batch-Verarbeitung über Nacht
- Cache-Verzeichnis regelmäßig leeren

---

## 📜 **LIZENZ & CREDITS**

Basiert auf:
- OpenAI Whisper (Speech Recognition)
- pyannote.audio (Speaker Diarization)
- spaCy (NLP)
- Praat/Parselmouth (Prosody Analysis)

---

**System bereit für Produktivbetrieb!**

*Letzte Aktualisierung: 2025-11-13*
