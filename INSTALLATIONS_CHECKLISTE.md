# ✅ INSTALLATIONS-CHECKLISTE

## SOFORT durchführen BEVOR Sie das System der Kundin geben!

---

## 1. **Python-Pakete installieren**

```bash
cd /home/dyai/Dokumente/DYAI_home/DEV/TOOLS/TransSemantic/Super_semantic_whisper

# Core packages
pip install spacy
python -m spacy download de_core_news_sm

# Falls nicht installiert:
pip install openai-whisper
pip install pyannote.audio
pip install torch torchaudio
```

---

## 2. **Hugging Face Token konfigurieren**

Für **Sprechertrennung** wird ein Token benötigt!

### Token erstellen:
1. Gehe zu: https://huggingface.co/join
2. Erstelle Account
3. Akzeptiere:
   - https://huggingface.co/pyannote/segmentation-3.0
   - https://huggingface.co/pyannote/speaker-diarization-3.1
4. Erstelle Token: https://huggingface.co/settings/tokens

### Token speichern:
```bash
cd /home/dyai/Dokumente/DYAI_home/DEV/TOOLS/TransSemantic/Super_semantic_whisper
echo "HF_TOKEN=hf_DEIN_TOKEN_HIER" > .env
```

---

## 3. **SOFORT-TEST durchführen**

```bash
python3 SOFORT_TEST.py
```

**Erwartetes Ergebnis:**
```
✓ Audio gefunden
✓ Transkription fertig: X Segmente
✓ Sprechertrennung: 2 Sprecher
✓ Prosody: X Segmente analysiert
✓ Outputs generiert:
  - HTML: SOFORT_TEST.html (XX KB)
  - PDF: SOFORT_TEST.pdf (XX KB)
  - MARKDOWN: SOFORT_TEST.md (XX KB)
  - JSON: SOFORT_TEST.prosody.json (XX KB)
```

---

## 4. **HTML-Output prüfen**

```bash
# HTML im Browser öffnen
firefox Transkripte_LLM/SOFORT_TEST.html
# oder
google-chrome Transkripte_LLM/SOFORT_TEST.html
```

**Checkliste im HTML:**
- [ ] Sprechertrennung sichtbar (verschiedene Farben)
- [ ] Zeitstempel vorhanden
- [ ] Prosody-Marker vorhanden ([TEMPO↑], [PITCH↓], etc.)
- [ ] Text korrekt transkribiert
- [ ] Layout professionell

---

## 5. **SVT GUI testen**

```bash
python3 svt.py
```

**In der GUI:**
- [ ] Audio-Datei auswählen funktioniert
- [ ] Checkboxen funktionieren:
  - [ ] Prosody Analysis
  - [ ] Speaker Diarization
  - [ ] Emotion Analysis
- [ ] "Transkription starten" startet Verarbeitung
- [ ] Fortschrittsbalken funktioniert
- [ ] Ergebnis wird angezeigt

---

## 6. **Für Kundin vorbereiten**

### Dateien bereitstellen:
```bash
# Erstelle ZIP mit allem Nötigen
cd /home/dyai/Dokumente/DYAI_home/DEV/TOOLS/TransSemantic
zip -r SVT_FuerKundin.zip Super_semantic_whisper/ \
  -x "*.pyc" "*__pycache__*" "*/venv/*" "*/.git/*" "*.m4a" "*.wav"
```

### Dokumentation bereitstellen:
- [ ] `FÜR_KUNDIN_README.md` - Hauptanleitung
- [ ] `SPEAKER_DIARIZATION.md` - HF-Token-Setup
- [ ] `SOFORT_TEST.py` - Schnelltest
- [ ] Beispiel-HTML aus Test

### .env Datei vorbereiten:
```bash
# WICHTIG: Token NICHT ins ZIP!
# Kundin muss eigenen Token erstellen

# Stattdessen: .env.example erstellen
echo "# Hugging Face Token für Speaker Diarization" > .env.example
echo "# Erstelle Token auf: https://huggingface.co/settings/tokens" >> .env.example
echo "HF_TOKEN=dein_token_hier" >> .env.example
```

---

## 7. **Finale Checkliste**

### Funktionalität:
- [ ] spaCy installiert und de_core_news_sm geladen
- [ ] Hugging Face Token konfiguriert (.env)
- [ ] SOFORT_TEST.py erfolgreich durchgelaufen
- [ ] HTML-Output sieht professionell aus
- [ ] SVT GUI startet ohne Fehler
- [ ] Alle 4 Output-Formate (HTML, PDF, MD, JSON) werden generiert

### Dokumentation:
- [ ] FÜR_KUNDIN_README.md vorhanden
- [ ] SPEAKER_DIARIZATION.md vorhanden
- [ ] .env.example vorhanden (NICHT .env mit echtem Token!)
- [ ] Beispiel-HTML als Demo vorhanden

### Bereitstellung:
- [ ] ZIP erstellt: SVT_FuerKundin.zip
- [ ] ZIP getestet (entpacken und SOFORT_TEST laufen lassen)
- [ ] README mit Installations-Anleitung dabei

---

## 8. **Übergabe an Kundin**

### Email-Text Vorlage:

```
Betreff: SVT - Semantic Voice Transcriber - Bereitstellung

Sehr geehrte [Name],

anbei das SVT-System für Ihre therapeutischen Transkriptionen.

Installation:
1. ZIP entpacken
2. In FÜR_KUNDIN_README.md die Installationsanleitung folgen
3. Hugging Face Token erstellen und in .env speichern
4. SOFORT_TEST.py ausführen zum Test

Hauptfunktionen:
✓ Automatische Sprechertrennung
✓ Hochgenaue Spracherkennung (Whisper AI)
✓ Prosody-Analyse (Sprachmelodie, Tempo, Energie)
✓ HTML/PDF-Output mit professionellem Layout
✓ Turning Points Markierung

Bei Fragen stehe ich zur Verfügung.

Mit freundlichen Grüßen
```

---

## ⚠️ **WICHTIGE HINWEISE**

### NICHT ins Repository/ZIP committen:
- ❌ `.env` mit echtem Token
- ❌ Audio-Dateien (*.m4a, *.wav)
- ❌ Transkripte mit echten Patientendaten
- ❌ Memory-Profile mit echten Namen

### Kundin MUSS selbst erstellen:
- ✅ Eigenen Hugging Face Account
- ✅ Eigenen Token
- ✅ Eigene .env Datei

---

## 🔍 **FEHLERSUCHE**

### Falls SOFORT_TEST fehlschlägt:

**1. spaCy fehlt:**
```bash
pip install spacy
python -m spacy download de_core_news_sm
```

**2. Keine Sprechertrennung:**
- Prüfe .env Datei existiert
- Prüfe HF_TOKEN ist gültig
- Teste: `python -c "from pyannote.audio import Pipeline; print('OK')"`

**3. HTML-Output fehlt:**
```bash
pip install weasyprint
# Mac: brew install weasyprint
# Ubuntu: sudo apt-get install weasyprint
```

**4. Whisper fehlt:**
```bash
pip install openai-whisper
```

---

## ✅ **ABSCHLUSS-CHECK**

Alles OK wenn:
```
✓ SOFORT_TEST.py durchgelaufen ohne Fehler
✓ HTML-Output professionell aussieht
✓ Sprechertrennung funktioniert (mehrere Farben)
✓ Prosody-Marker sichtbar
✓ SVT GUI startet
✓ ZIP erstellt und getestet
✓ Dokumentation vollständig
```

**DANN KANN ES AN DIE KUNDIN!**

---

Zeitaufwand: ~15-30 Minuten für komplette Installation und Test
