@echo off
REM One-Click Starter für Semantic Voice Transcriber (SVT) - Windows
REM Doppelklick auf diese Datei startet die GUI

REM Wechsle ins richtige Verzeichnis
cd /d "%~dp0"

REM Starte die GUI
python svt.py

REM Halte das Fenster offen wenn ein Fehler auftritt
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Fehler beim Starten der GUI
    echo Drücke eine Taste zum Beenden...
    pause >nul
)
