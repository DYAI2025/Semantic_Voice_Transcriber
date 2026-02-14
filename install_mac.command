#!/bin/bash
# SVT Local - macOS Installer
# For therapists with Mac computers

set -e

echo "=============================================="
echo "   SVT Local - Therapie Transkription"
echo "   Installation für macOS"
echo "=============================================="
echo ""

# Check macOS version
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "⚠️  Dieses Script ist nur für macOS gedacht."
    exit 1
fi

echo "[1/5] Prüfe Python Installation..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 nicht gefunden."
    echo "   Bitte installieren von: https://python.org/downloads/"
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
echo "   ✓ Python $PYTHON_VERSION gefunden"

echo ""
echo "[2/5] Installiere Dependencies..."
echo "   (Dies kann einige Minuten dauern...)"

python3 -m pip install --upgrade pip setuptools wheel

# Core dependencies
python3 -m pip install --quiet \
    pywebview \
    openai-whisper \
    torch \
    pyannote.audio \
    librosa \
    ffmpeg-python \
    python-docx \
    reportlab \
    numpy

echo "   ✓ Dependencies installiert"

echo ""
echo "[3/5] Lade Whisper Model herunter..."
python3 -c "import whisper; whisper.load_model('medium')" 2>/dev/null || true

echo ""
echo "[4/5] Lade pyannote Diarization Model herunter..."
python3 -c "
from pyannote.audio import Pipeline
pipeline = Pipeline.from_pretrained('pyannote/speaker-diarization-3.1')
" 2>/dev/null || echo "   ⚠️  Diarization Model wird beim ersten Start heruntergeladen"

echo ""
echo "[5/5] Erstelle Programme..."

# Create Applications folder if needed
APPS_DIR="$HOME/Applications"
mkdir -p "$APPS_DIR"

# Create wrapper script
WRAPPER="$APPS_DIR/SVT Local.app/Contents/MacOS/run_svt.sh"
mkdir -p "$(dirname "$WRAPPER")"

cat > "$WRAPPER" << 'WRAPPER_EOF'
#!/bin/bash
cd "$(dirname "$0")/../../.."
python3 "$(dirname "$0")/../../../svt_local_mac.py"
WRAPPER_EOF

chmod +x "$WRAPPER"

# Create Info.plist
PLIST="$APPS_DIR/SVT Local.app/Contents/Info.plist"
cat > "$PLIST" << PLIST_EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>run_svt.sh</string>
    <key>CFBundleIdentifier</key>
    <string>com.svt.local</string>
    <key>CFBundleName</key>
    <string>SVT Local</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0</string>
    <key>CFBundleVersion</key>
    <string>1</string>
    <key>LSMinimumSystemVersion</key>
    <string>10.15</string>
    <key>NSHumanReadableCopyright</key>
    <string>Copyright © 2026 SVT Local. Für Therapeuten entwickelt.</string>
</dict>
</plist>
PLIST_EOF

echo ""
echo "=============================================="
echo "   ✓ Installation abgeschlossen!"
echo "=============================================="
echo ""
echo "Starten Sie SVT Local:"
echo "   1. Öffnen Sie den Finder"
echo "   2. Gehen Sie zu Programme (Applications)"
echo "   3. Doppelklick auf 'SVT Local'"
echo ""
echo "ODER im Terminal:"
echo "   python3 ~/svt_local_mac.py"
echo ""
echo "💡 Tipp: Ziehen Sie Audio-Dateien direkt auf das App-Fenster"
echo ""
