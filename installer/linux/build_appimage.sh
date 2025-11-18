#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
APPDIR="$ROOT_DIR/dist/SVT.AppDir"
rm -rf "$APPDIR"
mkdir -p "$APPDIR/usr/bin"
cp -R "$ROOT_DIR" "$APPDIR/usr/share/svt"
cat > "$APPDIR/usr/bin/svt" <<'LAUNCHER'
#!/usr/bin/env bash
cd "$(dirname "$0")/../share/svt"
./svt_env/bin/python3 scripts/setup_local_stack.py --env .env --overwrite-env
./svt_env/bin/python3 svt.py
LAUNCHER
chmod +x "$APPDIR/usr/bin/svt"
cat > "$APPDIR/svt.desktop" <<'DESKTOP'
[Desktop Entry]
Name=SVT
Exec=svt
Icon=svt
Type=Application
Categories=AudioVideo;
DESKTOP
cp "$ROOT_DIR/start_svt.png" "$APPDIR/svt.png" 2>/dev/null || true
echo "Run appimagetool to pack $APPDIR"
