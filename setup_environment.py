#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WhisperSprecherMatcher - Environment Setup
Installiert alle notwendigen Abhängigkeiten und richtet das System ein
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def run_command(cmd, description):
    """Führe Command aus mit Fehlerbehandlung"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} erfolgreich")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} fehlgeschlagen: {e}")
        print(f"Output: {e.stdout}")
        print(f"Error: {e.stderr}")
        return False

def check_python_version():
    """Prüfe Python-Version"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python 3.8+ erforderlich. Aktuelle Version: {version.major}.{version.minor}")
        return False
    else:
        print(f"✅ Python {version.major}.{version.minor} erkannt")
        return True

def check_system_dependencies():
    """Prüfe System-Abhängigkeiten"""
    print("🔍 Prüfe System-Abhängigkeiten...")
    
    # FFmpeg prüfen
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        print("✅ FFmpeg ist installiert")
        ffmpeg_ok = True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("⚠️  FFmpeg nicht gefunden")
        ffmpeg_ok = False
    
    # Homebrew für macOS
    if platform.system() == "Darwin" and not ffmpeg_ok:
        print("💡 Auf macOS kann FFmpeg mit Homebrew installiert werden:")
        print("   brew install ffmpeg")
    
    return ffmpeg_ok

def install_python_packages():
    """Installiere Python-Pakete"""
    print("📦 Installiere Python-Pakete...")
    
    # Aktualisiere pip
    if not run_command(f"{sys.executable} -m pip install --upgrade pip", "pip Update"):
        return False
    
    # Installiere Requirements
    requirements_path = Path(__file__).parent / "requirements.txt"
    if requirements_path.exists():
        cmd = f"{sys.executable} -m pip install -r {requirements_path}"
        if not run_command(cmd, "Requirements Installation"):
            return False
    else:
        # Fallback: Installiere Pakete einzeln
        packages = [
            "openai-whisper",
            "PyYAML",
            "pathlib2",
            "watchdog",
            "requests",
            "numpy",
            "librosa",
            "soundfile"
        ]
        
        for package in packages:
            cmd = f"{sys.executable} -m pip install {package}"
            if not run_command(cmd, f"Installation von {package}"):
                print(f"⚠️ Warnung: {package} konnte nicht installiert werden")
    
    return True

def setup_directory_structure():
    """Erstelle Verzeichnisstruktur"""
    print("📁 Erstelle Verzeichnisstruktur...")
    
    base_path = Path("./whisper_speaker_matcher")
    directories = [
        base_path / "Eingang",
        base_path / "Memory",
        base_path / "logs"
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        print(f"📂 Erstellt: {directory}")
    
    return True

def test_installation():
    """Teste die Installation"""
    print("🧪 Teste Installation...")
    
    try:
        import whisper
        print("✅ Whisper importiert")
    except ImportError:
        print("❌ Whisper konnte nicht importiert werden")
        return False
    
    try:
        import yaml
        print("✅ YAML importiert")
    except ImportError:
        print("❌ YAML konnte nicht importiert werden")
        return False
    
    try:
        # Teste Whisper-Modell-Download
        print("🔄 Lade kleines Whisper-Modell (für Test)...")
        model = whisper.load_model("tiny")
        print("✅ Whisper-Modell erfolgreich geladen")
    except Exception as e:
        print(f"⚠️ Whisper-Modell-Test fehlgeschlagen: {e}")
        # Das ist nicht kritisch, das System kann trotzdem funktionieren
    
    return True

def create_launcher_script():
    """Erstelle Launcher-Skript"""
    print("🚀 Erstelle Launcher-Skript...")
    
    launcher_content = '''#!/bin/bash
# WhisperSprecherMatcher Launcher

echo "🎤 WhisperSprecherMatcher Launcher"
echo "=================================="
echo "1) Audio transkribieren"
echo "2) Memory aus Transkriptionen aufbauen"
echo "3) Exit"
echo ""
read -p "Wähle Option (1-3): " option

case $option in
    1)
        echo "Starte Auto-Transkription..."
        python3 auto_transcriber.py
        ;;
    2)
        echo "Starte Memory Builder..."
        python3 build_memory_from_transcripts.py
        ;;
    3)
        echo "Beende..."
        exit 0
        ;;
    *)
        echo "Ungültige Option"
        ;;
esac
'''
    
    launcher_path = Path("./whisper_speaker_matcher/start.sh")
    with open(launcher_path, 'w') as f:
        f.write(launcher_content)
    
    # Mache ausführbar
    launcher_path.chmod(0o755)
    print(f"✅ Launcher erstellt: {launcher_path}")

    return True


def create_platform_service_scripts():
    """Prepare platform-aware startup scripts for the transcription service."""
    service_command = f"{sys.executable} -m uvicorn services.transcription_service.api:app --host 0.0.0.0 --port 8000"
    system = platform.system()

    if system == "Windows":
        script_path = Path("start_transcription_service.bat")
        script_path.write_text(f"@echo off\n{service_command}\n")
    else:
        script_path = Path("start_transcription_service.sh")
        script_path.write_text(f"#!/bin/bash\n{service_command}\n")
        script_path.chmod(0o755)

    print(f"✅ Service-Startskript erstellt: {script_path}")

    # Add minimal permissions for macOS/Linux desktop entries
    if system in {"Darwin", "Linux"}:
        desktop_launcher = Path("start_transcription_service.desktop")
        desktop_launcher.write_text(
            "[Desktop Entry]\n"
            "Type=Application\n"
            "Name=Semantic Voice Transcription Service\n"
            f"Exec={script_path}\n"
            "Terminal=true\n"
        )
        desktop_launcher.chmod(0o755)
        print(f"✅ Desktop Launcher aktualisiert: {desktop_launcher}")

    return True

def main():
    """Hauptfunktion"""
    print("🎤 WhisperSprecherMatcher Setup")
    print("=" * 40)
    
    # System-Checks
    if not check_python_version():
        sys.exit(1)
    
    system_ok = check_system_dependencies()
    
    # Setup
    steps = [
        ("Verzeichnisstruktur erstellen", setup_directory_structure),
        ("Python-Pakete installieren", install_python_packages),
        ("Installation testen", test_installation),
        ("Launcher-Skript erstellen", create_launcher_script),
        ("Plattform-Startskripte für Service erstellen", create_platform_service_scripts)
    ]
    
    for description, func in steps:
        print(f"\n🔄 {description}...")
        if not func():
            print(f"❌ {description} fehlgeschlagen")
            print("Setup wird abgebrochen")
            sys.exit(1)
    
    print("\n" + "=" * 40)
    print("✅ Setup erfolgreich abgeschlossen!")
    print("\n📋 Nächste Schritte:")
    print("1. Audio-Dateien in 'whisper_speaker_matcher/Eingang/' legen")
    print("2. './whisper_speaker_matcher/start.sh' ausführen")
    
    if not system_ok:
        print("\n⚠️  Hinweise:")
        print("- FFmpeg installieren für bessere Audio-Konvertierung")
        print("  macOS: brew install ffmpeg")
        print("  Ubuntu: sudo apt install ffmpeg")
    
    print("\n🎉 Viel Erfolg mit dem WhisperSprecherMatcher!")

if __name__ == "__main__":
    main() 