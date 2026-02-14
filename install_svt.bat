@echo off
REM SVT Local - Quick Start für Therapeuten
REM 1. Python installieren: https://python.org
REM 2. Dependencies installieren
REM 3. Diese Datei ausführen

echo.
echo ========================================
echo    SVT Local - Therapie Transkription
echo ========================================
echo.
echo [1/3] Installiere Abhängigkeiten...

pip install --quiet PySimpleGUI openai-whisper torch pyannote.audio librosa ffmpeg-python python-docx reportlab

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo FEHLER: Installation fehlgeschlagen.
    echo Bitte pip und Python installieren.
    pause
    exit /b 1
)

echo.
echo [2/3] Starte SVT Local GUI...

python "%~dp0svt_local_gui.py"

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo FEHLER: SVT Local konnte nicht starten.
    pause
    exit /b 1
)

echo.
echo SVT Local wurde beendet.
pause
