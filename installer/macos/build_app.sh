#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
APP_DIR="$ROOT_DIR/dist/SVT.app"
MACOS_DIR="$APP_DIR/Contents/MacOS"
RESOURCES_DIR="$APP_DIR/Contents/Resources"
PYTHON_BIN="${PYTHON_BIN:-python3}"

clean_previous_build() {
    rm -rf "$APP_DIR"
    mkdir -p "$MACOS_DIR" "$RESOURCES_DIR"
}

copy_project_sources() {
    if ! command -v rsync >/dev/null 2>&1; then
        echo "❌ rsync wird benötigt (macOS: brew install rsync)" >&2
        exit 1
    fi

    rsync -a "$ROOT_DIR"/ "$RESOURCES_DIR"/ \
        --exclude 'dist' \
        --exclude '.git' \
        --exclude '__pycache__' \
        --exclude '*.log' \
        --exclude '*.pyc' \
        --exclude '.mypy_cache' \
        --exclude '.venv'
}

create_virtualenv() {
    if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
        echo "❌ Python (python3) wurde nicht gefunden. Bitte installieren." >&2
        exit 1
    fi

    echo "📦 Erstelle virtuelle Umgebung..."
    "$PYTHON_BIN" -m venv "$RESOURCES_DIR/svt_env"

    echo "⬆️  Aktualisiere pip..."
    "$RESOURCES_DIR/svt_env/bin/python3" -m pip install --upgrade pip

    if [[ -f "$RESOURCES_DIR/requirements.txt" ]]; then
        echo "📥 Installiere requirements.txt..."
        "$RESOURCES_DIR/svt_env/bin/pip" install -r "$RESOURCES_DIR/requirements.txt"
    fi

    if [[ -f "$RESOURCES_DIR/requirements_emotion.txt" ]]; then
        echo "📥 Installiere requirements_emotion.txt..."
        "$RESOURCES_DIR/svt_env/bin/pip" install -r "$RESOURCES_DIR/requirements_emotion.txt"
    fi
}

write_plist() {
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
}

write_launcher() {
    cat > "$MACOS_DIR/svt-launcher" <<'LAUNCHER'
#!/usr/bin/env bash
cd "$(dirname "$0")/../Resources"

./svt_env/bin/python3 scripts/setup_local_stack.py --env .env --overwrite-env
./svt_env/bin/python3 svt.py
LAUNCHER
    chmod +x "$MACOS_DIR/svt-launcher"
}

main() {
    clean_previous_build
    copy_project_sources
    create_virtualenv
    write_plist
    write_launcher
    echo "✅ App Bundle erstellt unter: $APP_DIR"
    echo "💡 Öffne SVT.app, um die Anwendung zu starten."
}

main
