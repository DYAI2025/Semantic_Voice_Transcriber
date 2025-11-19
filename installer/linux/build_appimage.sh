#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd ""+"$(dirname "$0")/../.." && pwd)"
APPDIR="$ROOT_DIR/dist/SVT.AppDir"

# Clean previous AppDir
rm -rf "$APPDIR"

# Create necessary AppDir layout
mkdir -p "$APPDIR/usr/bin"
mkdir -p "$APPDIR/usr/share/svt"

# Copy repository files into AppDir share directory
# Prefer rsync if available so we can exclude things like .git and dist
if command -v rsync >/dev/null 2>&1; then
  rsync -a --exclude='dist' --exclude='.git' --exclude='installer/linux' --exclude='__pycache__' "$ROOT_DIR/" "$APPDIR/usr/share/svt/"
else
  # Fallback to cp: copy only visible files and directories
  cp -R "$ROOT_DIR"/* "$APPDIR/usr/share/svt/" || true
fi

# Create launcher in usr/bin
cat > "$APPDIR/usr/bin/svt" <<'LAUNCHER'
#!/usr/bin/env bash
cd "$(dirname "$0")/../share/svt"
./svt_env/bin/python3 scripts/setup_local_stack.py --env .env --overwrite-env
./svt_env/bin/python3 svt.py
LAUNCHER
chmod +x "$APPDIR/usr/bin/svt"

# Desktop file
cat > "$APPDIR/svt.desktop" <<'DESKTOP'
[Desktop Entry]
Name=SVT
Exec=svt
Icon=svt
Type=Application
Categories=AudioVideo;
DESKTOP

# Copy icon if present
cp "$ROOT_DIR/start_svt.png" "$APPDIR/svt.png" 2>/dev/null || true

echo "Run appimagetool to pack $APPDIR"
