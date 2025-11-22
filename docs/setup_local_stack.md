# Lokale SVT-Stack-Initialisierung

**Last Updated:** 2025-11-19 | **Verified against commit:** 75fdfbbc

Dieses Skript automatisiert die wichtigsten Schritte, um Semantic Voice Transcriber für nicht‑technische Nutzer:innen vorzubereiten.

## Voraussetzungen
- Python 3.12+
- Ollama-Binary installiert oder per Installer mitgeliefert
- GGUF-Modellname (Standard: `qwen2.5-coder:7b`)

## Verwendung
```
python3 scripts/setup_local_stack.py \
    --env .env \
    --model qwen2.5-coder:7b
```
Optionen:
- `--overwrite-env`: überschreibt bestehende `.env` Dateien
- `--ollama /pfad/zu/ollama`: expliziter Pfad zur ollama CLI (falls sie nicht im PATH liegt)

## Was wird erledigt?
1. Legt Verzeichnisse `Eingang/`, `Transkripte_LLM/`, `Memory/` an und prüft Schreibrechte.
2. Erzeugt `.env` mit Offline-Defaults (`OPENAI_API_PROFILE=local`, `OLLAMA_BASE_URL=http://localhost:11434`).
3. Überprüft die Ollama-Installation und lädt das gewünschte Modell via `ollama pull` (falls notig).
4. Führt den Health-Check (`svt_core.health_check`) aus und zeigt eine zusammenfassende Statusübersicht.

Schlägt ein Schritt fehl, gibt das Skript konkrete Hinweise (z. B. „Ollama nicht gefunden“ oder „zu wenig Speicherplatz“).

## Integration in Installer
- Windows/.nsi: im `Section`-Block nach dem Kopieren der Dateien `python3 scripts\setup_local_stack.py --env "$INSTDIR\.env" --overwrite-env` ausführen.
- macOS/.pkg, Linux/.deb: `postinstall` Script ruft dasselbe Kommando auf.

Siehe auch `installer/windows/svt_lite.nsi` für eine Referenz-Integration.
