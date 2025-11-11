#!/bin/bash
# One-Click Starter für Therapeutic Transcription GUI
# Doppelklick auf diese Datei startet die GUI

# Wechsle ins richtige Verzeichnis
cd "$(dirname "$0")"

# Starte die GUI
python3 therapeutic_transcriber_gui.py

# Halte das Fenster offen wenn ein Fehler auftritt
if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Fehler beim Starten der GUI"
    echo "Drücke Enter zum Beenden..."
    read
fi
