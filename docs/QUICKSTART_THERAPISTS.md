# SVT Kurz-Anleitung

## Schnellstart in 5 Minuten

### 1. Starten

```bash
cd Semantic_Voice_Transcriber
python svt_local_gui.py
```

### 2. Audio laden

- Klick auf "Durchsuchen"
- Audio-Datei auswählen (MP3, WAV, M4A)
- Oder: Datei in `Eingang/PatientenName/` ablegen

### 3. Analysieren

- ✅ Prosodie (empfohlen)
- ✅ Sprechererkennung
- ✅ ATO-Marker
- Klick auf "Transkription starten"

### 4. Ergebnisse

- Im Dashboard ansehen: `http://localhost:8080`
- Exportieren als PDF/DOCX

---

## Wichtige Marker

| Marker | Bedeutung |
|--------|-----------|
| [HED] | Hedge (Unsicherheit) |
| [SIL] | Schweigen |
| [INS] | Erkenntnismoment |
| [PROJ] | Projektion |
| [TC] | Themenwechsel |
| [EMO] | Emotionaler Wendepunkt |

---

## Quick-Tipps

- **Gute Qualität:** Klare Aufnahme, wenig Hintergrundgeräusche
- **Memory:** Gleiche Patienten in denselben Ordner → System lernt
- **Confidence prüfen:** Scores unter 0.6 manuell prüfen
- **Datenschutz:** Alles bleibt lokal auf Ihrem Computer

---

## Mehr wissen?

→ Vollständiges Handbuch: `docs/BENUTZERHANDBUCH.md`
