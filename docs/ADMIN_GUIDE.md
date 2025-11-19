# Admin Guide

## Komponenten
- **SVT App**: installiert unter `Program Files/SVT` bzw. `/usr/share/svt`.
- **Python Runtime**: innerhalb `svt_env/` gebündelt.
- **Provisioning Script**: `scripts/setup_local_stack.py`
- **Health Check**: `svt_core.health_check`, beim Start obligatorisch.

## Automatisierte Provisionierung
```
python3 scripts/setup_local_stack.py --env <pfad> --overwrite-env
```
- Legt `.env` mit `OPENAI_API_PROFILE=local` an, prüft Ollama + Modell, testet Health Check.
- Log-Ausgabe zeigt Directory/Premissions/Disk-Status.

## Provider-Konfiguration
- `.env` Variablen: `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GOOGLE_PROJECT_ID`, `GROK_API_KEY` usw.
- GUI-Einstellungen schreiben verschlüsselte Schlüssel in die Config (TODO: implement once settings UI ready).
- ProviderManager fällt automatisch auf `local-ollama` zurück.

## Logs
- Transkriptions-Logs: `transcription_v4_emotion.log`
- Health-Check-Resultate: `logs/health_check*.log` (TODO once integrated).
- Dashboard errors: `/tmp/svt.log` (Linux/macOS) bzw. `%TEMP%\svt.log` (Windows).

## Uninstall
- Windows: Standard „Apps & Features“ (NSIS-Uninstaller entfernt Dateien und Desktop-Links).
- macOS: `SVT.app` löschen.
- Linux: `sudo apt purge svt` oder AppImage-Datei löschen.
