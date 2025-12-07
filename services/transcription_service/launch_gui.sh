#!/bin/bash
# Launch Standalone Transcription GUI
# This script checks dependencies and launches the GUI

echo "=========================================="
echo "Standalone Transcription Service GUI"
echo "=========================================="
echo ""

# Check if in correct directory
if [ ! -f "services/transcription_service/gui.py" ]; then
    echo "❌ Error: Please run this script from the repository root"
    echo "   cd /home/user/Semantic_Voice_Transcriber"
    exit 1
fi

# Check Python version
echo "Checking Python version..."
python3 --version || {
    echo "❌ Error: Python 3 not found"
    exit 1
}

# Check core dependencies
echo ""
echo "Checking core dependencies..."

MISSING_DEPS=()

python3 -c "import tkinter" 2>/dev/null || MISSING_DEPS+=("python3-tk")
python3 -c "import numpy" 2>/dev/null || MISSING_DEPS+=("numpy")
python3 -c "import whisper" 2>/dev/null || MISSING_DEPS+=("openai-whisper")
python3 -c "import librosa" 2>/dev/null || MISSING_DEPS+=("librosa")
python3 -c "import soundfile" 2>/dev/null || MISSING_DEPS+=("soundfile")

if [ ${#MISSING_DEPS[@]} -gt 0 ]; then
    echo ""
    echo "❌ Missing core dependencies:"
    for dep in "${MISSING_DEPS[@]}"; do
        echo "   - $dep"
    done
    echo ""
    echo "Install with:"
    echo "   pip install numpy openai-whisper librosa soundfile"
    echo "   sudo apt install python3-tk  # For Ubuntu/Debian"
    echo ""
    exit 1
fi

echo "✅ Core dependencies OK"

# Check optional dependencies
echo ""
echo "Checking optional dependencies (speaker detection)..."

OPTIONAL_MISSING=()
python3 -c "import pyannote.audio" 2>/dev/null || OPTIONAL_MISSING+=("pyannote.audio")
python3 -c "import torch" 2>/dev/null || OPTIONAL_MISSING+=("torch")

if [ ${#OPTIONAL_MISSING[@]} -gt 0 ]; then
    echo "⚠️  Speaker detection not available (missing: ${OPTIONAL_MISSING[*]})"
    echo "   Install with: pip install pyannote.audio torch"
    echo "   GUI will work without speaker detection"
else
    echo "✅ Speaker detection available"

    # Check HF token
    if [ -z "$HF_TOKEN" ] && [ ! -f ".env" ]; then
        echo "⚠️  HF_TOKEN not set - speaker detection won't work"
        echo "   Set token in .env file or environment variable"
    elif [ -f ".env" ] && grep -q "HF_TOKEN=" ".env"; then
        echo "✅ HF_TOKEN configured in .env"
    else
        echo "✅ HF_TOKEN set in environment"
    fi
fi

# Launch GUI
echo ""
echo "=========================================="
echo "Launching GUI..."
echo "=========================================="
echo ""

export PYTHONPATH="${PYTHONPATH}:$(pwd)"
python3 services/transcription_service/gui.py

echo ""
echo "GUI closed"
