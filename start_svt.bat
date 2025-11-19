@echo off
REM One-Click Starter for Semantic Voice Transcriber (SVT) - Windows
REM Double-click this file to start the GUI

REM Change to script directory
cd /d "%~dp0"

REM Start the GUI
python svt.py

REM Keep window open if error occurs
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Error starting GUI
    echo Press any key to exit...
    pause >nul
)
