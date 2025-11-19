"""Default configuration values for local-first SVT deployments."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict


@dataclass
class DefaultPaths:
    input_dir: Path = Path("Eingang")
    output_dir: Path = Path("Transkripte_LLM")
    memory_dir: Path = Path("Memory")


DEFAULT_ENV: Dict[str, str] = {
    "OPENAI_API_PROFILE": "local",
    "OPENAI_API_KEY": "",
    "OPENAI_API_KEY_ALIAS": "local",
    "OPENAI_DASHBOARD_MODEL": "",
    "ANTHROPIC_API_KEY": "",
    "GOOGLE_API_KEY": "",
    "GROK_API_KEY": "",
    "HF_TOKEN": "",
    "OLLAMA_BASE_URL": "http://localhost:11434",
    "OLLAMA_MODEL": "qwen2.5-coder:7b",
}
