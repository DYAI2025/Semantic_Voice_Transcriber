# SVT Installation (Endnutzer)

**Last Updated:** 2025-11-19 | **Verified against commit:** 75fdfbbc

1. **Installer herunterladen** (z. B. `SVT-Lite-Setup.exe`, `SVT.dmg`, `SVT.AppImage`)
2. **Installationsprogramm starten**
   - Windows: Standard-Setup folgt; am Ende entsteht eine Desktop-Verknüpfung.
   - macOS: SVT.app in den Programme-Ordner ziehen.
   - Linux: `.deb` installieren oder AppImage ausführbar machen (`chmod +x`).
3. **Erster Start**
   - Beim ersten Start führt SVT einen System-Health-Check aus (Ollama erreichbar? Speicherplatz?).
   - Warnungen können übersprungen werden; Fehler müssen behoben werden (Dialog zeigt Details).
4. **Audio ablegen & starten**
   - Legen Sie WAV/MP3/M4A-Dateien in `Eingang/` ab.
   - Starten Sie SVT über das Startmenü oder Desktop-Symbol.
   - Wählen Sie Dateien und starten Sie die Transkription. Dashboard/Provider-Einstellungen finden Sie im Settings-Menü.

Für Cloud-Modelle (OpenAI, Anthropic, Google, Grok) öffnen Sie **Einstellungen → Provider**, tragen den Schlüssel ein und klicken auf „Test“. Ohne Schlüssel bleibt SVT im lokalen Modus.
