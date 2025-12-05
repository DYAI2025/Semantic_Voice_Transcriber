from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

import httpx

from .transcription_service import TranscriptionRequest

logger = logging.getLogger(__name__)


@dataclass
class ProsodyAdapter:
    client: Any

    def attach(self, raw_result: Dict[str, Any], request: TranscriptionRequest) -> Any:
        if hasattr(self.client, "extract_from_segments"):
            return self.client.extract_from_segments(
                Path(request.audio_path), raw_result.get("segments", [])
            )
        return None


@dataclass
class AsyncPipelineClient:
    """Minimal REST client so other pipelines can call the new service."""

    base_url: str = "http://localhost:8000"
    timeout: float = 30.0

    async def transcribe(
        self,
        audio_path: Path,
        language: str = "de",
        model_profile: str = "base",
        initial_prompt: Optional[str] = None,
    ) -> Dict[str, Any]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            files = {"file": (audio_path.name, audio_path.read_bytes())}
            data = {
                "language": language,
                "model_profile": model_profile,
                "initial_prompt": initial_prompt or "",
                "audio_path": str(audio_path),
            }
            response = await client.post(f"{self.base_url}/transcribe", files=files, data=data)
            response.raise_for_status()
            return response.json()

    def transcribe_sync(
        self,
        audio_path: Path,
        language: str = "de",
        model_profile: str = "base",
        initial_prompt: Optional[str] = None,
    ) -> Dict[str, Any]:
        return asyncio.get_event_loop().run_until_complete(
            self.transcribe(audio_path, language, model_profile, initial_prompt)
        )
