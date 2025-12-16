#!/bin/bash
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
