from __future__ import annotations

import os
from typing import Any, Dict

from vertexai.preview.generative_models import GenerativeModel
from vertexai import init as vertex_init

from svt_core.llm_provider.base import LLMProvider, LLMResponse


class GoogleProvider(LLMProvider):
    def __init__(self, project: str | None = None, location: str | None = None, model: str | None = None):
        super().__init__(name="google")
        project_id = project or os.environ.get("GOOGLE_PROJECT_ID")
        if not project_id:
            raise ValueError("GOOGLE_PROJECT_ID not set")
        location = location or os.environ.get("GOOGLE_LOCATION", "us-central1")
        vertex_init(project=project_id, location=location)
        self.model_name = model or os.environ.get("GOOGLE_MODEL", "gemini-pro")
        self.model = GenerativeModel(self.model_name)

    def generate(self, prompt: str, **kwargs: Any) -> LLMResponse:
        resp = self.model.generate_content(
            prompt,
            generation_config={
                "temperature": kwargs.get("temperature", 0.5),
                "max_output_tokens": kwargs.get("max_tokens", 1024),
            },
        )
        text = resp.text
        metadata = {"model": self.model_name}
        usage = getattr(resp, "usage", {})
        return LLMResponse(text=text, usage=usage, metadata=metadata)

    def health_check(self) -> Dict[str, Any]:
        try:
            self.model.count_tokens(["ping"])
            return {"status": "ok", "details": "Vertex reachable"}
        except Exception as exc:  # pragma: no cover
            return {"status": "error", "details": str(exc)}

    def describe(self) -> Dict[str, Any]:
        return {"name": self.name, "model": self.model_name}
