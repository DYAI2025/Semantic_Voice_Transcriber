#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Google Drive Sync für WhisperSprecherMatcher
Synchronisiert Dateien zwischen Google Drive und lokaler Kopie
"""

import os
import sys
import shutil
import time
import logging
from pathlib import Path
from datetime import datetime
import subprocess

# Logging Setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class GoogleDriveSync:
    def __init__(self, google_drive_path=None):
        # Use environment variable or provided path (cross-platform)
        if google_drive_path is None:
            google_drive_path = os.environ.get('GOOGLE_DRIVE_PATH')

        if google_drive_path:
            self.google_drive_path = Path(google_drive_path)
        else:
            # No Google Drive path configured - sync will be disabled
            self.google_drive_path = None
            logger.warning("Google Drive path not configured. Set GOOGLE_DRIVE_PATH environment variable to enable sync.")

        self.local_path = Path("./whisper_speaker_matcher")
        self.sync_timeout = 10  # Sekunden
        
    def check_google_drive_availability(self):
        """Prüfe ob Google Drive verfügbar ist"""
        try:
            # Check if Google Drive path is configured
            if self.google_drive_path is None:
                return False

            # Prüfe ob Pfad existiert und zugänglich ist
            if not self.google_drive_path.exists():
                return False
            
            # Teste Dateizugriff mit Timeout
            test_file = self.google_drive_path / "test_access.tmp"
            start_time = time.time()
            
            try:
                with open(test_file, 'w') as f:
                    f.write("test")
                test_file.unlink()  # Lösche Test-Datei
                
                elapsed = time.time() - start_time
                if elapsed > self.sync_timeout:
                    logger.warning(f"Google Drive langsam ({elapsed:.1f}s)")
                    return False
                    
                return True
                
            except (OSError, IOError) as e:
                logger.warning(f"Google Drive Zugriff fehlgeschlagen: {e}")
                return False
                
        except Exception as e:
            logger.error(f"Google Drive Verfügbarkeit prüfen fehlgeschlagen: {e}")
            return False
    
    def sync_from_google_drive(self):
        """Synchronisiere Dateien von Google Drive zur lokalen Kopie"""
        if not self.check_google_drive_availability():
            logger.warning("Google Drive nicht verfügbar - keine Synchronisation")
            return False
        
        logger.info("🔄 Synchronisiere von Google Drive...")
        
        try:
            # Erstelle lokale Verzeichnisse
            self.local_path.mkdir(exist_ok=True)
            (self.local_path / "Eingang").mkdir(exist_ok=True)
            (self.local_path / "Memory").mkdir(exist_ok=True)
            
            # Synchronisiere Memory-Dateien
            memory_source = self.google_drive_path / "Memory"
            memory_target = self.local_path / "Memory"
            
            if memory_source.exists():
                for yaml_file in memory_source.glob("*.yaml"):
                    try:
                        target_file = memory_target / yaml_file.name
                        
                        # Kopiere nur wenn Quelle neuer ist oder Ziel nicht existiert
                        if (not target_file.exists() or 
                            yaml_file.stat().st_mtime > target_file.stat().st_mtime):
                            
                            shutil.copy2(yaml_file, target_file)
                            logger.info(f"📄 Synchronisiert: {yaml_file.name}")
                            
                    except Exception as e:
                        logger.error(f"Fehler beim Synchronisieren von {yaml_file}: {e}")
            
            # Synchronisiere neueste Transkriptionen
            eingang_source = self.google_drive_path / "Eingang"
            eingang_target = self.local_path / "Eingang"
            
            if eingang_source.exists():
                # Nur neueste .txt Dateien (letzte 7 Tage)
                cutoff_time = time.time() - (7 * 24 * 60 * 60)
                
                for txt_file in eingang_source.rglob("*.txt"):
                    try:
                        if txt_file.stat().st_mtime > cutoff_time:
                            target_file = eingang_target / txt_file.name
                            
                            if (not target_file.exists() or 
                                txt_file.stat().st_mtime > target_file.stat().st_mtime):
                                
                                shutil.copy2(txt_file, target_file)
                                logger.info(f"📝 Transkription synchronisiert: {txt_file.name}")
                                
                    except Exception as e:
                        logger.error(f"Fehler beim Synchronisieren von {txt_file}: {e}")
            
            logger.info("✅ Synchronisation von Google Drive abgeschlossen")
            return True
            
        except Exception as e:
            logger.error(f"Synchronisation fehlgeschlagen: {e}")
            return False
    
    def sync_to_google_drive(self):
        """Synchronisiere lokale Änderungen zurück zu Google Drive"""
        if not self.check_google_drive_availability():
            logger.warning("Google Drive nicht verfügbar - Upload nicht möglich")
            return False
        
        logger.info("⬆️ Synchronisiere zu Google Drive...")
        
        try:
            # Synchronisiere Memory-Updates
            memory_source = self.local_path / "Memory"
            memory_target = self.google_drive_path / "Memory"
            
            if memory_source.exists() and memory_target.exists():
                for yaml_file in memory_source.glob("*.yaml"):
                    try:
                        target_file = memory_target / yaml_file.name
                        
                        # Upload wenn lokal neuer
                        if (not target_file.exists() or 
                            yaml_file.stat().st_mtime > target_file.stat().st_mtime):
                            
                            shutil.copy2(yaml_file, target_file)
                            logger.info(f"⬆️ Memory hochgeladen: {yaml_file.name}")
                            
                    except Exception as e:
                        logger.error(f"Upload-Fehler für {yaml_file}: {e}")
            
            # Synchronisiere neue Transkriptionen
            eingang_source = self.local_path / "Eingang"
            eingang_target = self.google_drive_path / "Eingang"
            
            if eingang_source.exists() and eingang_target.exists():
                for txt_file in eingang_source.glob("*.txt"):
                    try:
                        target_file = eingang_target / txt_file.name
                        
                        if not target_file.exists():
                            shutil.copy2(txt_file, target_file)
                            logger.info(f"⬆️ Transkription hochgeladen: {txt_file.name}")
                            
                    except Exception as e:
                        logger.error(f"Upload-Fehler für {txt_file}: {e}")
            
            logger.info("✅ Upload zu Google Drive abgeschlossen")
            return True
            
        except Exception as e:
            logger.error(f"Upload fehlgeschlagen: {e}")
            return False
    
    def watch_for_google_drive(self, callback=None):
        """Überwache Google Drive Verfügbarkeit"""
        logger.info("👀 Überwache Google Drive Verfügbarkeit...")
        
        was_available = self.check_google_drive_availability()
        logger.info(f"Google Drive Status: {'✅ Verfügbar' if was_available else '❌ Nicht verfügbar'}")
        
        while True:
            time.sleep(30)  # Prüfe alle 30 Sekunden
            
            is_available = self.check_google_drive_availability()
            
            # Status geändert
            if is_available != was_available:
                if is_available:
                    logger.info("🟢 Google Drive ist wieder verfügbar!")
                    self.sync_from_google_drive()
                    if callback:
                        callback("google_drive_available")
                else:
                    logger.warning("🔴 Google Drive ist nicht mehr verfügbar")
                    if callback:
                        callback("google_drive_unavailable")
                
                was_available = is_available
    
    def force_sync(self):
        """Erzwinge Synchronisation in beide Richtungen"""
        logger.info("🔄 Erzwinge Vollsynchronisation...")
        
        success = True
        
        # Download von Google Drive
        if not self.sync_from_google_drive():
            success = False
        
        # Upload zu Google Drive
        if not self.sync_to_google_drive():
            success = False
        
        if success:
            logger.info("✅ Vollsynchronisation erfolgreich")
        else:
            logger.warning("⚠️ Synchronisation teilweise fehlgeschlagen")
        
        return success
    
    def status_report(self):
        """Erstelle Status-Bericht"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'google_drive_available': self.check_google_drive_availability(),
            'local_files': {
                'memory_files': len(list((self.local_path / "Memory").glob("*.yaml"))) if (self.local_path / "Memory").exists() else 0,
                'transcription_files': len(list((self.local_path / "Eingang").glob("*.txt"))) if (self.local_path / "Eingang").exists() else 0
            }
        }
        
        if report['google_drive_available']:
            try:
                report['google_drive_files'] = {
                    'memory_files': len(list((self.google_drive_path / "Memory").glob("*.yaml"))),
                    'transcription_files': len(list((self.google_drive_path / "Eingang").glob("*.txt")))
                }
            except:
                report['google_drive_files'] = None
        
        return report

def main():
    """Hauptfunktion"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Google Drive Sync für WhisperSprecherMatcher")
    parser.add_argument("--sync", action="store_true", help="Einmalige Synchronisation")
    parser.add_argument("--watch", action="store_true", help="Überwache Google Drive")
    parser.add_argument("--status", action="store_true", help="Zeige Status")
    parser.add_argument("--force", action="store_true", help="Erzwinge Synchronisation")
    
    args = parser.parse_args()
    
    sync = GoogleDriveSync()
    
    if args.status:
        report = sync.status_report()
        print("📊 Status Report:")
        print(f"🕒 Zeit: {report['timestamp']}")
        print(f"☁️ Google Drive: {'✅ Verfügbar' if report['google_drive_available'] else '❌ Nicht verfügbar'}")
        print(f"💾 Lokale Dateien: {report['local_files']['memory_files']} Memory, {report['local_files']['transcription_files']} Transkriptionen")
        if report.get('google_drive_files'):
            print(f"☁️ Google Drive Dateien: {report['google_drive_files']['memory_files']} Memory, {report['google_drive_files']['transcription_files']} Transkriptionen")
    
    elif args.sync:
        sync.sync_from_google_drive()
    
    elif args.force:
        sync.force_sync()
    
    elif args.watch:
        try:
            sync.watch_for_google_drive()
        except KeyboardInterrupt:
            print("\n👋 Google Drive Überwachung beendet")
    
    else:
        print("🔄 Google Drive Sync Tool")
        print("Optionen:")
        print("  --status   Zeige aktuellen Status")
        print("  --sync     Synchronisiere von Google Drive")
        print("  --force    Erzwinge Vollsynchronisation")
        print("  --watch    Überwache Google Drive kontinuierlich")

if __name__ == "__main__":
    main() 