#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🌟 Super Semantic Starter - Die Magie beginnt mit einem Klick!

⚠️  DEPRECATED: This launcher is deprecated.
    Please use the main SVT GUI instead: python3 svt.py
"""

import sys
import os
from pathlib import Path
import subprocess
import logging
import warnings

# Setup Logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

# Deprecation warning
warnings.warn(
    "start_super_semantic.py is deprecated. "
    "Please use 'python3 svt.py' for the unified GUI interface.",
    DeprecationWarning,
    stacklevel=2
)

logger.warning("\n" + "="*60)
logger.warning("⚠️  DEPRECATION WARNING")
logger.warning("="*60)
logger.warning("This launcher (start_super_semantic.py) is deprecated.")
logger.warning("Please use the main SVT GUI instead:")
logger.warning("  python3 svt.py")
logger.warning("="*60 + "\n")


def check_dependencies():
    """Prüfe und installiere fehlende Abhängigkeiten"""
    logger.info("🔍 Prüfe Abhängigkeiten...")
    
    required_packages = {
        'tkinter': 'tkinter',
        'yaml': 'pyyaml',
        'librosa': 'librosa',
        'textblob': 'textblob',
        'sklearn': 'scikit-learn',
        'numpy': 'numpy',
        'scipy': 'scipy'
    }
    
    missing = []
    
    for module, package in required_packages.items():
        try:
            if module == 'tkinter':
                import tkinter
            else:
                __import__(module)
            logger.info(f"✅ {module} verfügbar")
        except ImportError:
            missing.append(package)
            logger.warning(f"❌ {module} fehlt")
    
    if missing:
        logger.info("\n📦 Installiere fehlende Pakete...")
        for package in missing:
            if package != 'tkinter':  # tkinter muss manuell installiert werden
                logger.info(f"Installing {package}...")
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            else:
                logger.error("❌ tkinter muss manuell installiert werden!")
                logger.info("   macOS: brew install python-tk")
                logger.info("   Ubuntu: sudo apt-get install python3-tk")
                logger.info("   Windows: Sollte bereits installiert sein")
                return False
    
    logger.info("✅ Alle Abhängigkeiten installiert!\n")
    return True


def main():
    """Hauptfunktion"""
    print("""
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║     🌟 SUPER SEMANTIC PROCESSOR 🌟                      ║
║                                                          ║
║     Verwandle deine Chats in semantische Kunstwerke!    ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
    """)
    
    # Prüfe Abhängigkeiten
    if not check_dependencies():
        logger.error("\n❌ Bitte installiere die fehlenden Abhängigkeiten und starte erneut.")
        sys.exit(1)
    
    # Wähle Modus
    print("\n🎯 Wie möchtest du starten?\n")
    print("1. 🖥️  GUI-Modus (Empfohlen für Anfänger)")
    print("2. 🤖 Kommandozeilen-Modus (Für Fortgeschrittene)")
    print("3. 📚 Demo mit Beispieldaten")
    print("4. ❓ Hilfe anzeigen")
    print("5. 🚪 Beenden\n")
    
    choice = input("Wähle eine Option (1-5): ").strip()
    
    if choice == "1":
        # GUI starten
        logger.info("\n🚀 Starte GUI...")
        from super_semantic_gui import main as gui_main
        gui_main()
        
    elif choice == "2":
        # CLI-Modus
        logger.info("\n🤖 Kommandozeilen-Modus")
        
        # Frage nach Eingaben
        whatsapp = input("\nWhatsApp-Export Pfad (oder Enter für keine): ").strip()
        transcripts = input("Transkript-Ordner Pfad (oder Enter für Standard): ").strip() or "Transkripte_LLM"
        output = input("Ausgabe-Datei (oder Enter für Standard): ").strip() or "super_semantic_output.json"
        
        # Verarbeite
        from super_semantic_processor import process_everything
        
        logger.info("\n🔮 Starte Verarbeitung...")
        result = process_everything(
            whatsapp_export=Path(whatsapp) if whatsapp else None,
            transcript_dir=Path(transcripts) if transcripts else None,
            output_path=Path(output)
        )
        
        logger.info("\n✨ Fertig! Dateien erstellt:")
        logger.info(f"   - {output}")
        logger.info(f"   - {Path(output).with_suffix('.summary.md')}")
        
    elif choice == "3":
        # Demo-Modus
        logger.info("\n📚 Starte Demo...")
        
        # Erstelle Demo-Daten
        demo_dir = Path("demo_data")
        demo_dir.mkdir(exist_ok=True)
        
        # Erstelle Demo WhatsApp-Export
        demo_whatsapp = demo_dir / "demo_whatsapp.txt"
        with open(demo_whatsapp, 'w', encoding='utf-8') as f:
            f.write("""[28.06.24, 14:23:15] Max: Hey! Wie geht's dir heute? 😊
[28.06.24, 14:24:03] Anna: Hi Max! Mir geht's super, danke! Bin gerade vom Sport zurück 💪
[28.06.24, 14:24:45] Max: Cool! Was hast du denn gemacht?
[28.06.24, 14:25:12] Anna: War beim Yoga, total entspannend 🧘‍♀️
[28.06.24, 14:26:01] Max: Das klingt toll! Ich sollte auch mal wieder Sport machen...
[28.06.24, 14:26:33] Anna: Komm doch mal mit! Donnerstags um 18 Uhr
[28.06.24, 14:27:15] Max: Das ist eine super Idee! Ich bin dabei! 🎉
[28.06.24, 14:28:02] Anna: Freut mich! Wird bestimmt lustig 😄
[28.06.24, 14:28:45] Max: Auf jeden Fall! Bis Donnerstag dann!
[28.06.24, 14:29:10] Anna: Bis dann! Hab noch einen schönen Tag! ☀️
""")
        
        logger.info("✅ Demo-Daten erstellt")
        
        # Verarbeite Demo
        from super_semantic_processor import process_everything
        
        result = process_everything(
            whatsapp_export=demo_whatsapp,
            transcript_dir=Path("Transkripte_LLM") if Path("Transkripte_LLM").exists() else None,
            output_path=demo_dir / "demo_super_semantic.json"
        )
        
        logger.info(f"\n✨ Demo abgeschlossen! Ergebnisse in: {demo_dir}")
        
        # Zeige Zusammenfassung
        summary_file = demo_dir / "demo_super_semantic.summary.md"
        if summary_file.exists():
            logger.info("\n📄 ZUSAMMENFASSUNG:")
            logger.info("-" * 50)
            with open(summary_file, 'r', encoding='utf-8') as f:
                print(f.read())
                
    elif choice == "4":
        # Hilfe
        print("""
📚 HILFE - Super Semantic Processor

ÜBERBLICK:
Der Super Semantic Processor analysiert deine Chat-Verläufe und erstellt
eine tiefe semantische Analyse mit emotionalen Verläufen, Beziehungen
und thematischen Fäden.

FEATURES:
- 📱 WhatsApp-Export Analyse
- 🎤 Audio-Transkript Integration (mit Emotionen)
- 🏷️ Automatische Marker-Erkennung
- 🎭 Emotionale Verlaufsanalyse
- 🧵 Semantische Fäden-Identifikation
- 🔗 Beziehungs-Mapping

EINGABE-FORMATE:
1. WhatsApp-Export: Standard .txt Export aus WhatsApp
2. Transkripte: *_emotion_transkript.md Dateien aus Whisper V4

AUSGABE:
- JSON-Datei mit vollständiger semantischer Struktur
- Markdown-Zusammenfassung für Menschen

TIPPS:
- Nutze die GUI für eine einfache Bedienung
- Stelle sicher, dass deine Transkripte im richtigen Format sind
- Die Analyse kann bei vielen Nachrichten etwas dauern

WEITERE HILFE:
Siehe README.md für detaillierte Informationen
        """)
        
    elif choice == "5":
        logger.info("\n👋 Auf Wiedersehen!")
        sys.exit(0)
        
    else:
        logger.warning("\n❌ Ungültige Auswahl!")
        main()  # Neustart


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("\n\n👋 Programm beendet.")
    except Exception as e:
        logger.error(f"\n❌ Fehler: {e}")
        logger.exception("Details:")
        sys.exit(1) 