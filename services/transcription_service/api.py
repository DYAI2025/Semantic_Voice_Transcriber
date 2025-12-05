from __future__ import annotations

import logging
import tempfile
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, File, Form, UploadFile
from fastapi.responses import JSONResponse

from .config import TranscriptionConfig
from .model_manager import ModelProfile
from .transcription_service import (
    TranscriptionRequest,
    TranscriptionService,
    mark_low_confidence_segments,
)

logger = logging.getLogger(__name__)

app = FastAPI(title="Semantic Voice Transcriber", version="1.0.0")
service = TranscriptionService(TranscriptionConfig.from_env())


@app.post("/transcribe")
async def transcribe(
    file: UploadFile = File(...),
    language: str = Form("de"),
    model_profile: str = Form("base"),
    initial_prompt: Optional[str] = Form(None),
    audio_path: Optional[str] = Form(None),
):
    with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as tmp:
        tmp.write(await file.read())
        tmp_path = Path(tmp.name)

    try:
        request = TranscriptionRequest(
            audio_path=tmp_path,
            language=language,
            model_profile=ModelProfile(name=model_profile),
            initial_prompt=initial_prompt,
        )

        result = service.transcribe(request)
        payload = {
            "text": result.text,
            "segments": result.segments,
            "confidence_scores": result.confidence_scores,
            "marked_text": mark_low_confidence_segments(result.__dict__),
            "source": audio_path or file.filename,
        }
        return JSONResponse(payload)
    finally:
        try:
            tmp_path.unlink(missing_ok=True)
        except Exception:
            logger.warning("Temporary audio file could not be deleted: %s", tmp_path)


@app.get("/health")
async def health():
    return {"status": "ok"}
