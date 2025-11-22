# Installation Guide - Semantic Voice Transcriber

**Last Updated:** 2025-11-20 | **Verified against commit:** 992830d

This guide provides step-by-step installation instructions for the Semantic Voice Transcriber, including troubleshooting for common issues.

## Table of Contents

- [Quick Start](#quick-start)
- [Detailed Installation](#detailed-installation)
- [Speaker Diarization Setup](#speaker-diarization-setup)
- [Troubleshooting](#troubleshooting)
- [Virtual Environment (Recommended)](#virtual-environment-recommended)

---

## Quick Start

**Recommended: Use a virtual environment**

```bash
# Clone repository
git clone https://github.com/DYAI2025/Semantic_Voice_Transcriber.git
cd Semantic_Voice_Transcriber

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate  # Windows

# Install system dependencies (Ubuntu/Debian)
sudo apt install python3-pip ffmpeg portaudio19-dev python3-tk

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Manual installation for pyannote.audio (see below)
pip install pyannote.audio

# Launch SVT GUI
python3 svt.py
```

---

## Detailed Installation

### 1. System Dependencies

#### Ubuntu/Debian
```bash
sudo apt update
sudo apt install python3.12 python3-pip ffmpeg portaudio19-dev python3-tk
```

#### macOS
```bash
brew install python@3.12 ffmpeg portaudio
```

#### Windows
- Install Python 3.12+ from [python.org](https://www.python.org/downloads/)
- Install FFmpeg from [ffmpeg.org](https://ffmpeg.org/download.html)
- Add FFmpeg to PATH

### 2. Python Dependencies

#### Core Dependencies
```bash
pip install -r requirements.txt
```

This installs:
- ✅ Whisper STT engine
- ✅ Prosody analysis (librosa, parselmouth, scipy)
- ✅ Emotion detection (textblob)
- ✅ Output formatting (reportlab, weasyprint)
- ✅ LLM integration (openai)

#### Prosody Analysis (Phase 2c)

The "Big 4" prosody features (Tempo, Pitch, Energy, Pauses) require:

```bash
pip install librosa>=0.11.0 soundfile>=0.13.1 praat-parselmouth>=0.4.6 scipy>=1.16.0
```

**Verification:**
```bash
python3 -c "from prosody_extractor import ProsodyExtractor; print('✅ Prosody OK')"
```

### 3. Speaker Diarization (pyannote.audio)

**⚠️ IMPORTANT:** pyannote.audio may require manual installation due to a `julius` package build issue.

#### Method 1: Standard Installation (Try First)
```bash
pip install pyannote.audio
```

#### Method 2: Manual Installation (If Method 1 Fails)

If you encounter `AttributeError: install_layout` during `julius` build:

```bash
# Option A: Install julius separately
pip install --ignore-installed julius
pip install pyannote.audio

# Option B: Install from source
pip install git+https://github.com/adefossez/julius.git
pip install pyannote.audio

# Option C: Skip julius (for inference only, no augmentation)
pip install pyannote.audio --no-deps
pip install asteroid-filterbanks einops huggingface-hub lightning matplotlib \
    opentelemetry-api opentelemetry-exporter-otlp opentelemetry-sdk \
    pyannote-core pyannote-database pyannote-metrics pyannote-pipeline \
    pyannoteai-sdk pytorch-metric-learning rich safetensors torchmetrics \
    lightning-utilities pytorch-lightning cycler contourpy kiwisolver
```

**Verification:**
```bash
python3 -c "import pyannote.audio; print(f'✅ pyannote.audio {pyannote.audio.__version__}')"
```

---

## Speaker Diarization Setup

Speaker diarization requires a **Hugging Face token** to download pre-trained models.

### Step 1: Create Hugging Face Account
Visit https://huggingface.co/join and create a free account.

### Step 2: Accept Model Agreements
You must accept the user agreements for these models:
- https://huggingface.co/pyannote/segmentation-3.0
- https://huggingface.co/pyannote/speaker-diarization-3.1

Click "Agree and access repository" on each page.

### Step 3: Create Access Token
1. Go to https://huggingface.co/settings/tokens
2. Click "New token"
3. Name: `svt_diarization` (or any name)
4. Type: **Read**
5. Click "Generate token"
6. **Copy the token** (starts with `hf_...`)

### Step 4: Configure Token

Create a `.env` file in the project root:

```bash
echo "HF_TOKEN=hf_YourTokenHere" > .env
```

Or manually create `.env`:
```bash
# Semantic Voice Transcriber - Environment Configuration

# Hugging Face Token for Speaker Diarization
# Get token from: https://huggingface.co/settings/tokens
HF_TOKEN=hf_YourTokenHere

# Optional: OpenAI API Key for GPT-4 Psychoanalysis Dashboard
# Get key from: https://platform.openai.com/api-keys
# OPENAI_API_KEY=sk-YourKeyHere
```

**Security:** Add `.env` to `.gitignore` to avoid committing secrets!

### Step 5: Verify Setup

```bash
python3 -c "
from dotenv import load_dotenv
import os
load_dotenv()
assert os.getenv('HF_TOKEN'), '❌ HF_TOKEN not found in .env'
print('✅ HF_TOKEN configured')
"
```

---

## Troubleshooting

### FFmpeg Not Found
**Error:** `FileNotFoundError: [Errno 2] No such file or directory: 'ffmpeg'`

**Solution:**
```bash
# Ubuntu/Debian
sudo apt install ffmpeg

# macOS
brew install ffmpeg

# Windows
# Download from https://ffmpeg.org/download.html and add to PATH

# Verify
ffmpeg -version
```

### pyannote.audio Permission Denied
**Error:** `403 Client Error: Forbidden for url: https://huggingface.co/pyannote/...`

**Solution:**
1. Ensure you accepted model agreements (see Step 2 above)
2. Check HF_TOKEN is correct in `.env`
3. Token must have **Read** permissions
4. Wait 5 minutes after accepting agreements (cache refresh)

### julius Build Fails
**Error:** `AttributeError: install_layout. Did you mean: 'install_platlib'?`

**Solution:** This is a known setuptools compatibility issue. Use Method 2 or 3 from [Speaker Diarization Setup](#3-speaker-diarization-pyanno teamaudio) above.

### Low Transcription Quality
**Issue:** Transcriptions have many errors or low confidence scores.

**Solutions:**
1. Check audio quality (SNR > 10dB recommended)
2. Use higher Whisper model:
   ```python
   # In svt.py or auto_transcriber_v4_emotion.py
   model_size = "medium"  # or "large" for best quality
   ```
3. Enable audio preprocessing (noise reduction)
4. Check `transcription_v4_emotion.log` for warnings

### Memory Profile Not Updating
**Issue:** Speaker profiles in `Memory/` directory not updating.

**Solutions:**
1. Verify write permissions: `ls -la Memory/`
2. Check YAML syntax: `python3 test_yaml_structure.py`
3. Review logs for serialization errors
4. Ensure speaker name is valid (no special characters)

### Ollama Connection Failed
**Error:** `ConnectionError: [Errno 111] Connection refused` when using Psychoanalysis Dashboard.

**Solution:**
```bash
# Install Ollama (one-time)
curl -fsSL https://ollama.com/install.sh | sh

# Start Ollama server
ollama serve

# Download model
ollama pull qwen2.5-coder:7b

# Verify
curl http://localhost:11434/api/version
```

### ImportError After Update
**Error:** `ModuleNotFoundError: No module named 'xyz'`

**Solution:**
```bash
# Upgrade pip and reinstall
pip install --upgrade pip
pip install --force-reinstall -r requirements.txt
```

---

## Virtual Environment (Recommended)

Using a virtual environment prevents dependency conflicts with system packages.

### Why Use Virtual Environment?
- ✅ Isolated dependencies (won't affect system Python)
- ✅ Easier to manage different projects
- ✅ Safer experimentation
- ✅ Reproducible installations

### Setup Virtual Environment

```bash
# Create virtual environment
python3 -m venv .venv

# Activate (Linux/Mac)
source .venv/bin/activate

# Activate (Windows)
.venv\Scripts\activate

# Your prompt should now show (.venv)
(.venv) user@machine:~/Semantic_Voice_Transcriber$

# Install dependencies
pip install -r requirements.txt

# When done, deactivate
deactivate
```

### Auto-Activate (Optional)

Add to `.bashrc` or `.zshrc`:
```bash
# Auto-activate venv when entering project directory
cd() {
    builtin cd "$@"
    if [[ -d .venv ]]; then
        source .venv/bin/activate
    fi
}
```

---

## Verification Checklist

After installation, verify all features:

```bash
# 1. Core transcription
python3 -c "import whisper; print('✅ Whisper')"

# 2. Prosody analysis
python3 -c "from prosody_extractor import ProsodyExtractor; print('✅ Prosody')"

# 3. Speaker diarization
python3 -c "import pyannote.audio; print('✅ pyannote.audio')"

# 4. Output formatting
python3 -c "from output_formatter import OutputFormatter; print('✅ Output Formatter')"

# 5. LLM integration
python3 -c "import openai; print('✅ OpenAI')"

# 6. Launch GUI
python3 svt.py
```

**Expected Output:**
```
✅ Whisper
✅ Prosody
✅ pyannote.audio
✅ Output Formatter
✅ OpenAI
[GUI window opens]
```

---

## Getting Help

- **Documentation:** See `docs/` directory for detailed guides
- **Issues:** Report bugs at https://github.com/DYAI2025/Semantic_Voice_Transcriber/issues
- **Feature Audit:** Run `python3 -m audit.cli` to check feature status
- **Logs:** Check `transcription_v4_emotion.log` for errors

---

## Next Steps

1. ✅ Configure HF_TOKEN for speaker diarization
2. ✅ (Optional) Configure OPENAI_API_KEY for psychoanalysis
3. ✅ Place audio files in `Eingang/Patient/`
4. ✅ Launch `python3 svt.py`
5. ✅ Click "Transkription starten"

**For advanced usage, see:**
- `CLAUDE.md` - AI assistant development guide
- `SPEAKER_DIARIZATION.md` - Diarization details
- `PSYCHOANALYSIS_DASHBOARD.md` - Dashboard guide
- `THERAPEUTIC_TRANSCRIPT_FORMAT.md` - Output format guide
