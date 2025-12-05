from __future__ import annotations

import asyncio
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

from .adapters import AsyncPipelineClient


@dataclass
class PipelineIntegrationResult:
    transcription: Dict[str, Any]
    extras: Dict[str, Any]


async def run_pipeline_with_service(
    audio_path: Path,
    client: Optional[AsyncPipelineClient] = None,
    language: str = "de",
    model_profile: str = "base",
    initial_prompt: Optional[str] = None,
    prosody_enricher: Optional[Any] = None,
    marker_adapter: Optional[Any] = None,
) -> PipelineIntegrationResult:
    client = client or AsyncPipelineClient()
    transcription = await client.transcribe(audio_path, language, model_profile, initial_prompt)

    extras: Dict[str, Any] = {}
    if prosody_enricher:
        extras["prosody"] = prosody_enricher(transcription)
    if marker_adapter:
        extras["markers"] = marker_adapter(transcription)

    return PipelineIntegrationResult(transcription=transcription, extras=extras)


def run_pipeline_with_service_sync(
    audio_path: Path,
    client: Optional[AsyncPipelineClient] = None,
    language: str = "de",
    model_profile: str = "base",
    initial_prompt: Optional[str] = None,
    prosody_enricher: Optional[Any] = None,
    marker_adapter: Optional[Any] = None,
) -> PipelineIntegrationResult:
    return asyncio.run(
        run_pipeline_with_service(
            audio_path,
            client=client,
            language=language,
            model_profile=model_profile,
            initial_prompt=initial_prompt,
            prosody_enricher=prosody_enricher,
            marker_adapter=marker_adapter,
        )
    )
