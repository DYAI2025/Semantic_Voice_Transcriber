# Installation & Setup Guide
## Cross-Platform Installation für Semantic Voice Transcriber (SVT)

**Last Updated:** 2025-11-19 | **Verified against commit:** 75fdfbbc

Diese Anleitung hilft Ihnen, SVT auf **Windows**, **macOS** oder **Linux** zu installieren und zu starten.

---

## 📋 Systemanforderungen

- **Python**: 3.9 oder höher (empfohlen: 3.11)
- **RAM**: Mindestens 8 GB (16 GB empfohlen für große Modelle)
- **Speicherplatz**: 5-10 GB für Whisper-Modelle
- **Internet**: Für Download der Modelle und Dependencies

---

## 🐧 Linux Installation (Ubuntu/Debian)

### 1. System-Dependencies installieren

```bash
# Update package list
sudo apt update

# Install Python 3.11+ and required system packages
sudo apt install python3.11 python3-pip python3-venv python3-tk ffmpeg portaudio19-dev build-essential

# Verify Python version
python3 --version  # Should be 3.9+
```

### 2. Python Virtual Environment erstellen (empfohlen)

```bash
# Navigate to project directory
cd /path/to/Semantic_Voice_Transcriber

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate
```

### 3. Python-Dependencies installieren

```bash
# Install core dependencies
pip install -r requirements.txt

# Install emotion analysis dependencies (optional, but recommended)
pip install -r requirements_emotion.txt

# Verify installation
python3 -c "import whisper; print('Whisper OK')"
```

### 4. SVT starten

```bash
# Option 1: Using start script (recommended)
chmod +x start_svt.sh
./start_svt.sh

# Option 2: Direct Python execution
python3 svt.py
```

### Troubleshooting Linux

**Problem: "ModuleNotFoundError: No module named 'tkinter'"**
```bash
sudo apt install python3-tk
```

**Problem: "FFmpeg not found"**
```bash
sudo apt install ffmpeg
ffmpeg -version  # Verify installation
```

**Problem: "librosa installation fails"**
```bash
sudo apt install libsndfile1 libsndfile1-dev
pip install librosa soundfile
```

---

## 🍎 macOS Installation

### 1. Homebrew installieren (falls noch nicht vorhanden)

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### 2. System-Dependencies installieren

```bash
# Install Python 3.11
brew install python@3.11

# Install FFmpeg
brew install ffmpeg

# Install PortAudio (for audio processing)
brew install portaudio

# Verify installations
python3 --version  # Should be 3.11+
ffmpeg -version
```

### 3. Python Virtual Environment erstellen (empfohlen)

```bash
# Navigate to project directory
cd /path/to/Semantic_Voice_Transcriber

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate
```

### 4. Python-Dependencies installieren

```bash
# Install core dependencies
pip install -r requirements.txt

# Install emotion analysis dependencies (optional, but recommended)
pip install -r requirements_emotion.txt

# Verify installation
python3 -c "import whisper; print('Whisper OK')"
```

### 5. SVT starten

```bash
# Option 1: Using start script (recommended)
chmod +x start_svt.sh
./start_svt.sh

# Option 2: Direct Python execution
python3 svt.py
```

### Troubleshooting macOS

**Problem: "command not found: python3"**
```bash
# Use full path or create alias
/usr/local/bin/python3.11 svt.py

# Or add to ~/.zshrc or ~/.bash_profile:
alias python3='/usr/local/bin/python3.11'
```

**Problem: "tkinter module not found"**
```bash
# Tkinter is usually included with Python on macOS
# If missing, reinstall Python with Homebrew
brew reinstall python@3.11
```

**Problem: "SSL certificate verification failed"**
```bash
# Run Python certificate installer
/Applications/Python\ 3.11/Install\ Certificates.command
```

---

## 🪟 Windows Installation

### 1. Python installieren

1. Download Python 3.11+ von [python.org/downloads](https://www.python.org/downloads/)
2. **WICHTIG**: Während der Installation "Add Python to PATH" aktivieren
3. Installation abschließen

Verify in Command Prompt (cmd):
```cmd
python --version
```

### 2. FFmpeg installieren

**Option A: Using Chocolatey (empfohlen)**
```powershell
# Install Chocolatey (if not already installed)
# Run PowerShell as Administrator
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# Install FFmpeg
choco install ffmpeg

# Verify
ffmpeg -version
```

**Option B: Manual Installation**
1. Download FFmpeg von [ffmpeg.org/download.html#build-windows](https://ffmpeg.org/download.html#build-windows)
2. Extrahieren Sie das Archiv (z.B. nach `C:\ffmpeg`)
3. Fügen Sie `C:\ffmpeg\bin` zu Ihrer PATH-Umgebungsvariable hinzu:
   - Systemsteuerung → System → Erweiterte Systemeinstellungen
   - Umgebungsvariablen → Path → Bearbeiten → Neu → `C:\ffmpeg\bin`
4. Neustart des Terminals

### 3. Python Virtual Environment erstellen (empfohlen)

```cmd
REM Navigate to project directory
cd C:\path\to\Semantic_Voice_Transcriber

REM Create virtual environment
python -m venv venv

REM Activate virtual environment
venv\Scripts\activate
```

### 4. Python-Dependencies installieren

```cmd
REM Install core dependencies
pip install -r requirements.txt

REM Install emotion analysis dependencies (optional)
pip install -r requirements_emotion.txt

REM Verify installation
python -c "import whisper; print('Whisper OK')"
```

### 5. SVT starten

```cmd
REM Option 1: Using batch script (recommended)
start_svt.bat

REM Option 2: Direct Python execution
python svt.py
```

### Troubleshooting Windows

**Problem: "python is not recognized as an internal or external command"**
- Python wurde nicht zu PATH hinzugefügt
- Neuinstallation mit "Add Python to PATH" Option
- Oder manuell Python-Pfad zu PATH hinzufügen

**Problem: "Microsoft Visual C++ 14.0 or greater is required"**
```cmd
# Install Microsoft C++ Build Tools
# Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/
# Select "Desktop development with C++"
```

**Problem: "ffmpeg not found"**
- Siehe FFmpeg Installation oben
- Stellen Sie sicher, dass FFmpeg in PATH ist
- Neustart des Terminals nach PATH-Änderung

**Problem: "torch installation fails"**
```cmd
# Install torch with CUDA support (if you have NVIDIA GPU)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# Or CPU-only version
pip install torch torchvision torchaudio
```

---

## 🎯 Speaker Diarization Setup (alle Plattformen)

Speaker Diarization (Sprechererkennung) benötigt einen Hugging Face Token:

### 1. Hugging Face Account erstellen

Gehen Sie zu [huggingface.co/join](https://huggingface.co/join)

### 2. Model-Zugriff akzeptieren

Akzeptieren Sie die Nutzungsbedingungen für:
- [pyannote/segmentation-3.0](https://huggingface.co/pyannote/segmentation-3.0)
- [pyannote/speaker-diarization-3.1](https://huggingface.co/pyannote/speaker-diarization-3.1)

### 3. Access Token erstellen

1. Gehen Sie zu [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)
2. Klicken Sie "New token"
3. Name: "SVT-Speaker-Diarization"
4. Type: "Read"
5. Kopieren Sie den Token (beginnt mit `hf_...`)

### 4. .env Datei erstellen

Erstellen Sie eine Datei `.env` im Projektverzeichnis:

**Linux/macOS:**
```bash
echo "HF_TOKEN=hf_YourTokenHere" > .env
```

**Windows (PowerShell):**
```powershell
Set-Content -Path ".env" -Value "HF_TOKEN=hf_YourTokenHere"
```

**Windows (cmd):**
```cmd
echo HF_TOKEN=hf_YourTokenHere > .env
```

Ersetzen Sie `hf_YourTokenHere` mit Ihrem echten Token.

---

## 🧪 Installation testen

### Quick Test

Starten Sie SVT und klicken Sie auf "🧪 Quick Test (erste Datei)":

```bash
# Linux/macOS
./start_svt.sh

# Windows
start_svt.bat
```

### Command-Line Test

```bash
# Test Whisper installation
python3 -c "import whisper; model = whisper.load_model('tiny'); print('✅ Whisper OK')"

# Test prosody analysis
python3 -c "from prosody_extractor import ProsodyExtractor; print('✅ Prosody OK')"

# Test speaker diarization (requires HF token)
python3 -c "from speaker_diarizer import SpeakerDiarizer; print('✅ Diarization OK')"

# Run integration test
python3 test_prosody_pipeline.py
```

---

## 📁 Verzeichnisstruktur vorbereiten

SVT erwartet folgende Verzeichnisstruktur:

```
Semantic_Voice_Transcriber/
├── Eingang/              # INPUT: Audio-Dateien hier ablegen
│   └── Patient/          # (Optional) Sprecher-spezifische Ordner
├── Transkripte_LLM/      # OUTPUT: Generierte Transkripte
├── Memory/               # Speaker-Profile (automatisch erstellt)
├── svt.py               # Haupt-GUI
├── start_svt.sh         # Linux/Mac Starter
└── start_svt.bat        # Windows Starter
```

Verzeichnisse werden automatisch erstellt, wenn SVT startet.

---

## 🚀 SVT starten - Übersicht

### Linux/macOS
```bash
# Im Terminal
./start_svt.sh

# Oder via Finder/File Manager: Doppelklick auf start_svt.sh
```

### Windows
```cmd
REM In Command Prompt
start_svt.bat

REM Oder via Explorer: Doppelklick auf start_svt.bat
```

### Alternative: Python direkt
```bash
# Alle Plattformen
python3 svt.py   # Linux/macOS
python svt.py    # Windows
```

---

## 🔧 Optionale Konfiguration

### Google Drive Sync (Optional)

Wenn Sie Google Drive Sync verwenden möchten:

**Linux/macOS:**
```bash
export GOOGLE_DRIVE_PATH="/path/to/your/google/drive/folder"
echo 'export GOOGLE_DRIVE_PATH="/path/to/your/google/drive/folder"' >> ~/.bashrc
```

**Windows:**
```cmd
setx GOOGLE_DRIVE_PATH "C:\Users\YourName\Google Drive\SVT"
```

### Whisper Model Cache

Standardmäßig lädt Whisper Modelle nach `~/.cache/whisper` herunter.

Ändern Sie den Cache-Pfad (optional):

**Linux/macOS:**
```bash
export WHISPER_CACHE="/custom/path/to/whisper_models"
```

**Windows:**
```cmd
setx WHISPER_CACHE "D:\whisper_models"
```

---

## 📊 Modell-Übersicht

| Modell | Größe | RAM | Genauigkeit | Geschwindigkeit |
|--------|-------|-----|-------------|-----------------|
| tiny   | 39M   | ~1GB | Niedrig | Sehr schnell |
| base   | 74M   | ~1GB | Mittel | Schnell |
| small  | 244M  | ~2GB | Gut | Moderat |
| medium | 769M  | ~5GB | Sehr gut | Langsam |
| large  | 1550M | ~10GB | Exzellent | Sehr langsam |

**Empfehlung für Therapie**: `medium` oder `large`

---

## ❓ Häufige Probleme

### "Out of Memory" Fehler
- Verwenden Sie ein kleineres Modell (tiny, base, small)
- Schließen Sie andere Anwendungen
- Erweitern Sie RAM oder verwenden Sie GPU

### Langsame Transkription
- Normale CPU-Transkription: 2-5x Echtzeit
- GPU beschleunigt: 10-20x Echtzeit
- Verwenden Sie kleinere Modelle für Tests

### Audio-Datei wird nicht erkannt
Unterstützte Formate: `.m4a`, `.opus`, `.wav`, `.mp3`, `.flac`, `.ogg`

Konvertierung mit FFmpeg:
```bash
ffmpeg -i input.m4a -ar 16000 output.wav
```

### GUI startet nicht
- Überprüfen Sie Python-Version: `python3 --version` (mind. 3.9)
- Überprüfen Sie tkinter: `python3 -c "import tkinter"`
- Siehe plattformspezifische Troubleshooting-Abschnitte oben

---

## 📚 Weiterführende Dokumentation

- **Projekt-Übersicht**: `CLAUDE.md`
- **Speaker Diarization**: `SPEAKER_DIARIZATION.md`
- **Quick Start**: `README.md` (falls vorhanden)

---

## 🆘 Support

Bei Problemen:

1. Überprüfen Sie die Logs: `transcription_v4_emotion.log`
2. Lesen Sie die Troubleshooting-Abschnitte oben
3. Prüfen Sie Systemvoraussetzungen
4. Erstellen Sie ein Issue auf GitHub (falls verfügbar)

---

## ✅ Checkliste für erfolgreiche Installation

- [ ] Python 3.9+ installiert und in PATH
- [ ] FFmpeg installiert und in PATH
- [ ] Virtual Environment erstellt (optional, empfohlen)
- [ ] `requirements.txt` installiert
- [ ] `requirements_emotion.txt` installiert (optional)
- [ ] Hugging Face Token in `.env` (für Speaker Diarization)
- [ ] `Eingang/` Verzeichnis mit Test-Audio-Datei
- [ ] SVT startet ohne Fehler
- [ ] Quick Test erfolgreich

**Viel Erfolg mit Semantic Voice Transcriber!** 🎤
