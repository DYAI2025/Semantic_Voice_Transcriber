from __future__ import annotations

import logging
import os
import threading
from dataclasses import dataclass
from typing import Callable, Optional

from .config import TranscriptionConfig

logger = logging.getLogger(__name__)


@dataclass
class ModelProfile:
    name: str = "base"
    device_preference: Optional[str] = None


class ModelManager:
    """Load and cache Whisper models with basic device negotiation."""

    def __init__(
        self,
        config: Optional[TranscriptionConfig] = None,
        model_loader: Optional[Callable[..., object]] = None,
    ) -> None:
        self.config = config or TranscriptionConfig.from_env()
        self._model_loader = model_loader or self._default_loader
        self._cache = {}
        self._lock = threading.Lock()

    def _default_loader(self, model_size: str, device: Optional[str]):
        import whisper

        load_kwargs = {"device": device} if device else {}
        if self.config.cache_dir:
            load_kwargs["download_root"] = str(self.config.cache_dir)
        return whisper.load_model(model_size, **load_kwargs)

    def _resolve_device(self, device_preference: Optional[str]) -> Optional[str]:
        preferred = device_preference or os.getenv("SVT_DEVICE")
        if not preferred:
            try:
                import torch

                if torch.cuda.is_available():
                    return "cuda"
            except Exception:
                return None
            return None

        if preferred.lower() == "auto":
            return self._resolve_device(None)
        return preferred

    def load(self, profile: ModelProfile) -> object:
        device = self._resolve_device(profile.device_preference)
        cache_key = (profile.name, device)

        with self._lock:
            if cache_key in self._cache:
                return self._cache[cache_key]

            logger.info("Loading Whisper model %s on device %s", profile.name, device or "cpu")
            model = self._model_loader(profile.name, device)
            self._cache[cache_key] = model
            return model
