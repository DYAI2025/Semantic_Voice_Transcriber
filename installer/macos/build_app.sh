#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
APP_DIR="$ROOT_DIR/dist/SVT.app"
rm -rf "$APP_DIR"
mkdir -p "$APP_DIR/Contents/MacOS"
cp -R "$ROOT_DIR" "$APP_DIR/Contents/Resources"
cat > "$APP_DIR/Contents/Info.plist" <<'PLIST'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>svt-launcher</string>
    <key>CFBundleIdentifier</key>
    <string>com.semanticvoice.transcriber</string>
    <key>CFBundleName</key>
    <string>SVT</string>
    <key>CFBundleVersion</key>
    <string>1.0</string>
</dict>
</plist>
PLIST
cat > "$APP_DIR/Contents/MacOS/svt-launcher" <<'LAUNCHER'
#!/usr/bin/env bash
cd "$(dirname "$0")/../Resources"
./svt_env/bin/python3 scripts/setup_local_stack.py --env .env --overwrite-env
./svt_env/bin/python3 svt.py
LAUNCHER
chmod +x "$APP_DIR/Contents/MacOS/svt-launcher"
echo "App bundle created at $APP_DIR"
