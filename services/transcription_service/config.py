from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional


@dataclass
class TranscriptionConfig:
    """Configuration for the transcription service.

    Paths are injected via environment variables or optional YAML/JSON files
    to avoid hard-coded global locations.
    """

    input_dir: Path
    output_dir: Path
    log_dir: Path
    cache_dir: Optional[Path] = None

    @classmethod
    def from_env(cls, config_path: Optional[Path] = None) -> "TranscriptionConfig":
        if config_path and config_path.exists():
            return cls.from_file(config_path)

        base_dir = Path(os.getenv("SVT_BASE_PATH", "."))
        input_dir = Path(os.getenv("SVT_INPUT_DIR", base_dir / "Eingang"))
        output_dir = Path(os.getenv("SVT_OUTPUT_DIR", base_dir / "Transkripte_LLM"))
        log_dir = Path(os.getenv("SVT_LOG_DIR", base_dir / "logs"))
        cache_dir_env = os.getenv("SVT_MODEL_CACHE")

        return cls(
            input_dir=input_dir,
            output_dir=output_dir,
            log_dir=log_dir,
            cache_dir=Path(cache_dir_env) if cache_dir_env else None,
        )

    @classmethod
    def from_file(cls, config_path: Path) -> "TranscriptionConfig":
        import yaml

        with open(config_path, "r", encoding="utf-8") as handle:
            raw = yaml.safe_load(handle)

        return cls(
            input_dir=Path(raw.get("input_dir", "Eingang")),
            output_dir=Path(raw.get("output_dir", "Transkripte_LLM")),
            log_dir=Path(raw.get("log_dir", "logs")),
            cache_dir=Path(raw["cache_dir"]) if raw.get("cache_dir") else None,
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "input_dir": str(self.input_dir),
            "output_dir": str(self.output_dir),
            "log_dir": str(self.log_dir),
            "cache_dir": str(self.cache_dir) if self.cache_dir else None,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict())
