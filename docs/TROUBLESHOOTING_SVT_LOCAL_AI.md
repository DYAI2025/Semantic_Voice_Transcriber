# Troubleshooting SVT Local AI

**Last Updated:** 2025-11-19 | **Verified against commit:** 75fdfbbc

## Health Check Fehler
- **Ollama unreachable**: Prüfen, ob `ollama serve` läuft. Unter Windows ggf. einmal neu starten. Port 11434 darf nicht blockiert sein.
- **Directories not writable**: Installer erneut mit Admin-Rechten ausführen oder Installationspfad ändern.
- **Disk warning**: Mindestens 2 GB freien Speicher bereitstellen (Transkript & Modelle).

## Dashboard schlägt fehl / KeyError
- Cache-Datei unter `Transkripte_LLM/*_psychoanalysis_cache*` löschen und Dashboard neu starten.
- Bei Cloud-Provider: Keys im Settings-Dialog prüfen, „Test Provider“ ausführen.

## Sprechererkennung liefert keine Labels
- Ohne HF-Token nutzt SVT die CPU-Fallback-Diarisierung (weniger präzise, aber lokal). Pyannote kann in den Einstellungen deaktiviert oder mit gültigem Token reaktiviert werden.

## Installer bricht ab
- Windows: Virenscanner kann Exe blockieren → Ausnahmen setzen.
- macOS: Gatekeeper-Sperre → Rechtsklick → Öffnen → zustimmen; zukünftig notarisierten Build verwenden.
- Linux: fehlende `fuse`-Module für AppImage → `sudo apt install fuse`.

## Support-Log sammeln
- `transcription_v4_emotion.log`
- `/tmp/svt.log` (oder `%TEMP%\svt.log`)
- `.env` (ohne API-Keys) für Pfadkontrolle
