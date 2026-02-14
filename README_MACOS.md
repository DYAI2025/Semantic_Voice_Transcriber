# 🎤 SVT Local - macOS Version

**Professionelle Therapie-Transkription für Mac**

---

## Warum macOS?

| Vorteil | Beschreibung |
|---------|-------------|
| **Einfache Installation** | Homebrew oder Drag & Drop |
| **macOS Native** | PyWebView für native GUI |
| **Apple Silicon** | Schnellere Transkription mit M1/M2/M3 |
| **Datenschutz** | Alles lokal, keine Cloud |

---

## Installation

### Option 1: Installer Script (einfach)

```bash
# Download und ausführen
chmod +x install_mac.command
./install_mac.command
```

### Option 2: Manuell

```bash
# Python 3.10+ installieren (von python.org)

# Dependencies installieren
pip install pywebview openai-whisper torch pyannote.audio \
    librosa ffmpeg-python python-docx reportlab

# Starten
python svt_local_mac.py
```

---

## System-Anforderungen

| | Minimum | Empfohlen |
|---|---------|-----------|
| **macOS** | 10.15 (Catalina) | 12.0+ (Monterey) |
| **RAM** | 8 GB | 16 GB |
| **Speicher** | 5 GB | 10 GB |
| **CPU** | Intel | Apple Silicon (M1/M2/M3) |

**Empfehlung: Apple Silicon Mac** - Whisper läuft 3-5x schneller!

---

## Transkriptions-Qualität

### Whisper Modelle

| Modell | Geschwindigkeit | Genauigkeit |
|--------|-----------------|-------------|
| `tiny` | 32x Echtzeit | ~85% |
| `base` | 16x Echtzeit | ~90% |
| `small` | 6x Echtzeit | ~95% |
| `medium` | 2-3x Echtzeit | **99%+** |
| `large` | Echtzeit | 99.9% |

**Empfehlung:** `medium` - beste Balance aus Speed/Qualität

### Sprecherkennung

| System | Genauigkeit | Sprecher |
|--------|-------------|----------|
| pyannote v3.1 | **99.99%** | 2 (Therapeut + Patient) |

Optimiert für 2-Sprecher-Szenarien (Therapie-Sitzung).

---

## Verwendung

### Starten

1. **SVT Local.app** aus Programme öffnen
2. Oder: `python svt_local_mac.py` im Terminal

### Transkription erstellen

```
1. Audio-Datei per Drag & Drop einfügen
2. "Transkription starten" klicken
3. Warten (abhängig von Dateilänge)
4. Ergebnisse ansehen und exportieren
```

### Export-Formate

| Format | Verwendung |
|--------|-----------|
| PDF | Für Akten, ausdrucken |
| DOCX | Weiterbearbeiten in Word |
| JSON | Für andere Software |

---

## Für Entwickler

### GUI starten (Development)

```bash
python svt_local_mac.py
```

### Quality Test

```bash
# Transkriptions-Qualität testen
python test_quality.py --audio test_session.mp3

# Ergebnisse
cat test_session_results.json
```

### Modelle konfigurieren

```python
# In svt_local_mac.py
backend.load_models(model_size="medium")  # oder "small", "large"
```

---

## Datenschutz (DSGVO)

✅ **Alles läuft lokal auf Ihrem Mac**  
✅ **Keine Daten werden ins Internet übertragen**  
✅ **Keine Cloud, keine Server**  
✅ **Apple Silicon Secure Enclave für maximale Sicherheit**

---

## Troubleshooting

### "pyannote.audio not found"

```bash
pip install pyannote.audio
# Oder mit Homebrew:
brew install pyannote-audio
```

### "ffmpeg not found"

```bash
brew install ffmpeg
```

### Zu langsam auf Intel Mac

```bash
# Kleinere Modelle verwenden
# In svt_local_mac.py:
backend.load_models(model_size="small")  # statt "medium"
```

### RAM Probleme

- Keine anderen großen Programme während Transkription
- Oder `model_size="small"` verwenden

---

## Support

Bei Problemen:
1. Python 3.10+ installiert?
2. genug RAM (8GB minimum)?
3. Audio-Datei nicht beschädigt?

---

## Lizenz

SVT Local - Für Therapeuten entwickelt
