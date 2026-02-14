# SVT Projekt Plan - 2026-02-14

## Vision
**"Transkription der Welt für Therapeuten"**

## Zielgruppe
**Technikfremde Therapeuten** - Mac + Windows
- Kein CLI, kein Terminal
- Einfache, intuitive UI
- Alles selbsterklärend

---

## Plattformen

| Plattform | Status | GUI Framework |
|-----------|--------|---------------|
| **macOS** | 🆕 Neu | PyWebView (native-like) |
| **Windows** | ✅ Bestehend | PySimpleGUI |
| **Linux** | ⏳ Später | PyWebView |

---

## Transkriptions-Qualität

### Whisper Modelle

| Modell | Speed | Genauigkeit | RAM |
|--------|-------|-------------|-----|
| `tiny` | 32x | 85% | 1GB |
| `base` | 16x | 90% | 1.5GB |
| `small` | 6x | 95% | 2.5GB |
| **`medium`** | 2-3x | **99%+** | 5GB |
| `large` | 1x | 99.9% | 10GB |

**Empfehlung:** `medium` - beste Balance

### Sprecherkennung

| System | Genauigkeit | Spezialisierung |
|--------|-------------|-----------------|
| pyannote v3.1 | **99.99%** | 2 Sprecher (Therapeut + Patient) |

---

## Features nach Priorität

### Phase 1: Core (Diese Woche)
- [x] macOS GUI (PyWebView)
- [x] Windows GUI (PySimpleGUI)
- [ ] Transkription Accuracy Test
- [ ] Sprechertrennung Test
- [ ] PDF Export
- [ ] DOCX Export

### Phase 2: Intelligence (Nächste Woche)
- [ ] Claude/Gemini Summary
- [ ] ATO Marker Integration
- [ ] Prosody Analysis
- [ ] Therapeutische Vorschläge

### Phase 3: Deployment (Danach)
- [ ] macOS Installer (.app)
- [ ] Windows Installer (.exe)
- [ ] Deutscher Server (Cloud Backup)
- [ ] DSGVO Compliance

---

## Aktueller Stand (2026-02-14)

### ✅ Fertig
- svt_local_gui.py (Windows)
- svt_local_mac.py (macOS)
- install_svt.bat (Windows)
- install_mac.command (macOS)
- test_quality.py (Quality Tests)
- README_MACOS.md

### ⏳ In Arbeit
- PDF Export
- DOCX Export
- Quality Testing

### ⏳ Offen
- Cloud Backend
- User Accounts
- Sync Feature

---

## Dependencies

| Was | Status |
|-----|--------|
| openai-whisper | ✅ |
| pyannote.audio | ✅ |
| torch | ✅ |
| librosa | ✅ |
| pywebview | ✅ |
| Claude API | ⚠️ Key fehlt |
| Gemini API | ⚠️ Key fehlt |

---

## Installation

### macOS

```bash
chmod +x install_mac.command
./install_mac.command
# Oder:
python svt_local_mac.py
```

### Windows

```bash
# Doppelklick auf install_svt.bat
# Oder:
python svt_local_gui.py
```

---

## Quality Testing

```bash
# Transkriptions-Qualität testen
python test_quality.py --audio test_session.mp3

# Ergebnisse
cat test_session_results.json
```

---

## Timeline

| Phase | Zeit |
|-------|------|
| Phase 1 (Core) | 1 Woche |
| Phase 2 (Intelligence) | 2 Wochen |
| Phase 3 (Deployment) | 1 Woche |

**Total: ~4 Wochen für Complete Version**
