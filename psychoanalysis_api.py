# psychoanalysis_api.py
import json
import logging
import os
import random
import time
from pathlib import Path
from typing import Any, Callable, Optional

from openai import OpenAI

try:
    from openai import OpenAIError, RateLimitError  # type: ignore
except Exception:  # pragma: no cover - fallback for optional dependency
    class OpenAIError(Exception):
        """Fallback OpenAI error when SDK exceptions are unavailable."""

    class RateLimitError(OpenAIError):
        """Fallback rate-limit error."""

import yaml

# Try to load .env file if python-dotenv is available
try:
    from dotenv import load_dotenv
    load_dotenv()  # Load .env file from current directory
except ImportError:
    pass  # dotenv not installed, use environment variables only

logger = logging.getLogger(__name__)


class PsychoanalysisAPI:
    """OpenAI API client for psychoanalytic analysis using emotion-dynamics skill"""

    def __init__(
        self,
        config_path: str = "config/psychoanalysis_config.yaml",
        client: Optional[OpenAI] = None
    ):
        """Initialize API client with configuration"""
        with open(config_path) as f:
            self.config = yaml.safe_load(f)

        self.api_profile = os.environ.get("OPENAI_API_PROFILE", "primary")
        self.api_key_alias = os.environ.get("OPENAI_API_KEY_ALIAS") or self.api_profile

        api_key = self._resolve_api_key()
        if not api_key:
            raise ValueError(
                "No OpenAI API key configured. Set OPENAI_API_KEY or profile-specific"
                " OPENAI_API_KEY_<PROFILE>."
            )

        self.client = client or OpenAI(api_key=api_key)
        self.model = self._resolve_model()
        self.max_tokens = self.config["openai"]["max_tokens"]
        self.temperature = self.config["openai"]["temperature"]
        self.retry_max_attempts = int(
            os.environ.get(
                "DASHBOARD_MAX_RETRIES",
                str(self.config.get("retries", {}).get("max_attempts", 3))
            )
        )
        self.retry_base_delay = float(
            os.environ.get(
                "DASHBOARD_RETRY_BASE_DELAY",
                str(self.config.get("retries", {}).get("base_delay", 2.0))
            )
        )
        self.retry_max_delay = float(
            os.environ.get(
                "DASHBOARD_RETRY_MAX_DELAY",
                str(self.config.get("retries", {}).get("max_delay", 30.0))
            )
        )
        self.retry_jitter = float(
            os.environ.get(
                "DASHBOARD_RETRY_JITTER",
                str(self.config.get("retries", {}).get("jitter", 1.0))
            )
        )
        self.last_retry_count = 0

    def build_system_prompt(self, skill_path):
        """Build system prompt from SKILL.md"""
        with open(skill_path, encoding="utf-8") as f:
            skill_content = f.read()

        system_prompt = f"""Du bist ein Assistent für psychoanalytische Textanalyse.

Deine Aufgabe: Analysiere den gegebenen Transkript-Text mithilfe des folgenden Skills:

{skill_content}

Zusätzlich: Erkenne psychoanalytische Marker aus folgenden Kategorien:
- Abwehrmechanismen (defense): Verleugnung, Projektion, Rationalisierung, Verschiebung, Regression
- Widerstand (resistance): Schweigen, Themenwechsel, Humor, Absagen
- Übertragung (transference): positiv, negativ, erotisch
- Unbewusste Themen (theme): Trennungsangst, Kontrolle, Verlassenwerden, Scham/Schuld

Antworte NUR mit der strukturierten JSON-Ausgabe wie im Skill beschrieben."""

        return system_prompt

    def _resolve_api_key(self) -> Optional[str]:
        """Resolve API key for the configured profile."""
        profile_var = f"OPENAI_API_KEY_{self.api_profile.upper()}"
        return os.environ.get(profile_var) or os.environ.get("OPENAI_API_KEY")

    def _resolve_model(self) -> str:
        """Resolve dashboard model for configured profile."""
        profile_var = f"OPENAI_DASHBOARD_MODEL_{self.api_profile.upper()}"
        env_model = (
            os.environ.get(profile_var)
            or os.environ.get("OPENAI_DASHBOARD_MODEL")
        )
        return env_model or self.config["openai"]["model"]

    def build_user_prompt(self, transcript_data):
        """Build user prompt from transcript JSON"""
        user_prompt = f"""Analysiere folgendes Transkript:

**Metadaten:**
- Datei: {transcript_data['transcript_meta']['file']}
- Sprecher: {', '.join(transcript_data['transcript_meta']['speaker_labels'])}
- Dauer: {transcript_data['transcript_meta']['duration_seconds']}s

**Utterances:**
{json.dumps(transcript_data['utterances'], indent=2, ensure_ascii=False)}

Führe die vollständige Analyse durch und gib das Ergebnis im spezifizierten JSON-Format zurück."""

        return user_prompt

    def build_function_schema(self):
        """Build function calling schema for structured output"""
        return {
            "name": "analyze_transcript_ued_markers",
            "description": "Analyze transcript with UED emotion dynamics and psychoanalytic markers",
            "parameters": {
                "type": "object",
                "properties": {
                    "input_meta": {
                        "type": "object",
                        "properties": {
                            "language": {"type": "string"},
                            "text_type": {"type": "string"},
                            "notes": {"type": "string"}
                        }
                    },
                    "utterance_states": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "id": {"type": "integer"},
                                "speaker": {"type": "string"},
                                "order_index": {"type": "integer"},
                                "text": {"type": "string"},
                                "valence": {"type": "number"},
                                "arousal": {"type": "number"},
                                "dominance": {"type": "number"},
                                "discrete_emotions": {"type": "object"},
                                "confidence": {"type": "number"},
                                "markers": {
                                    "type": "array",
                                    "items": {"type": "string"}
                                }
                            },
                            "required": ["id", "text", "valence", "arousal", "markers"]
                        }
                    },
                    "ued_metrics": {
                        "type": "object",
                        "properties": {
                            "home_base": {"type": "object"},
                            "variability": {"type": "object"},
                            "instability": {"type": "object"},
                            "rise_rate": {"type": "object"},
                            "recovery_rate": {"type": "object"}
                        }
                    },
                    "marker_summary": {
                        "type": "object",
                        "properties": {
                            "frequencies": {"type": "object"},
                            "dominance_ranking": {
                                "type": "array",
                                "items": {"type": "string"}
                            }
                        }
                    },
                    "psychological_lenses": {"type": "object"},
                    "disclaimers": {"type": "object"}
                },
                "required": ["utterance_states", "ued_metrics", "marker_summary"]
            }
        }

    def _call_with_retry(self, func: Callable[[], Any]):
        """Execute API call with retry/backoff for rate limits."""
        attempt = 0
        self.last_retry_count = 0

        while True:
            attempt += 1
            try:
                result = func()
                self.last_retry_count = attempt - 1
                return result
            except RateLimitError as err:
                self.last_retry_count = attempt
                if attempt >= self.retry_max_attempts:
                    logger.error(
                        "OpenAI rate limit after %s attempts (alias=%s, model=%s)",
                        attempt,
                        self.api_key_alias,
                        self.model
                    )
                    raise

                delay = min(
                    self.retry_max_delay,
                    self.retry_base_delay * (2 ** (attempt - 1))
                )
                delay += random.uniform(0.0, self.retry_jitter)
                logger.warning(
                    "Rate limit hit (attempt %s/%s, alias=%s, model=%s). Retrying in %.2fs",
                    attempt,
                    self.retry_max_attempts,
                    self.api_key_alias,
                    self.model,
                    delay
                )
                time.sleep(delay)
            except OpenAIError:
                self.last_retry_count = attempt - 1
                raise

    def analyze_transcript(self, transcript_data, skill_path):
        """Send transcript to OpenAI API and return analysis"""
        system_prompt = self.build_system_prompt(skill_path)
        user_prompt = self.build_user_prompt(transcript_data)
        function_schema = self.build_function_schema()

        def _dispatch():
            return self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                functions=[function_schema],
                function_call={"name": "analyze_transcript_ued_markers"},
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )

        response = self._call_with_retry(_dispatch)

        # Extract function call result
        function_call = response.choices[0].message.function_call
        analysis = json.loads(function_call.arguments)

        return analysis
