"""Persistent settings management (GUI + env)."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict


@dataclass
class ProviderProfile:
    key: str = "local"
    model: str = ""
    alias: str = "local"
    extra: Dict[str, str] = field(default_factory=dict)


class SettingsStore:
    def __init__(self, path: Path = Path("settings.json")):
        self.path = path
        self.data: Dict[str, Dict] = {}
        self.load()

    def load(self) -> None:
        if self.path.exists():
            self.data = json.loads(self.path.read_text(encoding="utf-8"))
        else:
            self.data = {}

    def save(self) -> None:
        self.path.write_text(json.dumps(self.data, indent=2), encoding="utf-8")

    def get_provider_profile(self) -> ProviderProfile:
        profile = self.data.get("provider", {"key": "local"})
        return ProviderProfile(**profile)

    def set_provider_profile(self, profile: ProviderProfile) -> None:
        self.data["provider"] = profile.__dict__
        self.save()
