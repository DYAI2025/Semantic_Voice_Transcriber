# Local-First Installer & Provider Design

## Components
- **LLM Provider Layer** (`svt/llm_provider/`)
  - `LLMProvider` base class (`generate`, `health_check`, `name`).
  - Implementations: `LocalOllamaProvider` (default), `OpenAIProvider`, `AnthropicProvider`, `GoogleProvider`, `GrokProvider`.
  - `ProviderManager` selects provider based on settings, handles fallback, surfaces telemetry.
- **Health Check Module** (`svt/health_check.py`)
  - Runs before GUI boot. Checks: Ollama service reachable, bundled model exists, write permissions, optional cloud provider credentials.
  - Emits structured status (OK/WARN/ERROR) consumed by GUI and installer scripts.
- **Provisioning Script** (`scripts/setup_local_stack.py`)
  - Installs/validates Ollama, copies bundled GGUF model, generates `.env` with offline defaults, seeds directories.
- **Installer Support** (`installer/<os>/`)
  - OS-specific packages call the provisioning script during install and register uninstall actions.
- **Config Layer** (`svt/config/settings.py`)
  - Centralizes `.env` and GUI settings; exposes provider, directories, and feature toggles.

## Data & Control Flow
1. **Installer** runs provisioning script (install Ollama, copy model, generate config).
2. **App Launch** executes `svt.health_check.run_all()`.
   - On success → GUI starts with local provider selected.
   - On failure → Display modal with retry/auto-fix options (e.g., restart Ollama service) or allow advanced override.
3. **Runtime**
   - ProviderManager routes LLM requests; on exception, logs and auto-falls back to local provider.
   - Health widget in GUI shows current provider status (local OK / Cloud OK / Degraded).
   - Logs capture provider events, fallback counts, and health check results.

## Sequence (Installer → GUI)
1. User runs installer (`.exe`/`.pkg`/`.deb`).
2. Installer copies SVT bundle + Python runtime + Ollama assets; runs `setup_local_stack.py`.
3. First launch executes health check (blocking splash). If OK, main window loads; otherwise, user sees actionable guidance.
4. In settings, user can switch provider profile (local default). Provider test runs a short API call; success persists key encrypted on disk.

## Mapping to Requirements
- FR-1/FR-2: LocalOllamaProvider + provisioning ensure offline default.
- FR-3: CPU diarization & offline defaults eliminate Hugging Face requirement.
- FR-4/FR-13: Installer layer handles OS packaging, uninstaller, permissions.
- FR-5/FR-11/FR-14: Health check + status widget + logging.
- FR-6/FR-7/FR-8: Provider layer, settings UI, fallback manager.
- FR-9: Installer build matrix supports Lite (single GGUF) vs Full (additional models/resources).
- FR-10: CPU diarization component.
- FR-12: Provisioning script for administrators.
- FR-14: Health logs accessible under `logs/health_check*.json`.

SC Links: Health-check gating addresses SC-1, SC-4; Settings + provider activation covers SC-3; Installer tests cover SC-5; documentation + pilot tie into SC-2.
