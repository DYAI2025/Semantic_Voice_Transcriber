# psychoanalysis_api_ollama.py
"""Local-first psychoanalysis API built on top of the LLMProvider layer."""
from __future__ import annotations

import json
import logging
import yaml
from pathlib import Path
from typing import Any, Dict, List

from svt_core.llm_provider.local_ollama import LocalOllamaProvider, OllamaSettings

logger = logging.getLogger(__name__)


class OllamaPsychoanalysisAPI:
    """Wrapper that asks a local Ollama model to analyze transcripts."""

    def __init__(self, config_path: str = "config/psychoanalysis_config.yaml"):
        with open(config_path, encoding="utf-8") as f:
            self.config = yaml.safe_load(f)

        ollama_cfg = self.config.get("ollama", {})
        self.settings = OllamaSettings(
            base_url=ollama_cfg.get("base_url", "http://localhost:11434"),
            model=ollama_cfg.get("model", "qwen2.5-coder:7b"),
            temperature=ollama_cfg.get("temperature", 0.7),
            max_tokens=ollama_cfg.get("max_tokens", 4000),
        )
        self.provider = LocalOllamaProvider(self.settings)
        self._assert_local_stack()

    def _assert_local_stack(self) -> None:
        health = self.provider.health_check()
        if health["status"] == "error":
            raise ConnectionError(
                "❌ Ollama not reachable. Start `ollama serve` or install from https://ollama.com/download\n"
                f"Details: {health['details']}"
            )
        if health["status"] == "warn":
            logger.warning("Ollama health warning: %s", health["details"])

    def build_system_prompt(self, skill_path: Path) -> str:
        with open(skill_path, encoding="utf-8") as f:
            skill_content = f.read()
        return (
            "Du bist ein Assistent für psychoanalytische Textanalyse.\n\n"
            "Deine Aufgabe: Analysiere den gegebenen Transkript-Text mithilfe des folgenden Skills:\n\n"
            f"{skill_content}\n\n"
            "Zusätzlich: Erkenne psychoanalytische Marker aus folgenden Kategorien:\n"
            "- Abwehrmechanismen (defense)\n"
            "- Widerstand (resistance)\n"
            "- Übertragung (transference)\n"
            "- Unbewusste Themen (theme)\n\n"
            "WICHTIG: Antworte NUR mit der strukturierten JSON-Ausgabe wie im Skill beschrieben."
        )

    def build_user_prompt(self, transcript_data: Dict[str, Any]) -> str:
        return (
            "Analysiere folgendes Transkript:\n\n"
            f"**Metadaten:**\n- Datei: {transcript_data['transcript_meta']['file']}\n"
            f"- Sprecher: {', '.join(transcript_data['transcript_meta']['speaker_labels'])}\n"
            f"- Dauer: {transcript_data['transcript_meta']['duration_seconds']}s\n\n"
            f"**Utterances:**\n{json.dumps(transcript_data['utterances'], indent=2, ensure_ascii=False)}\n\n"
            "Führe die vollständige Analyse durch und gib das Ergebnis im spezifizierten JSON-Format zurück."
            " Antworte NUR mit dem JSON-Objekt, keine weiteren Texte."
        )

    def analyze_transcript(self, transcript_data: Dict[str, Any], skill_path: str) -> Dict[str, Any]:
        system_prompt = self.build_system_prompt(Path(skill_path))
        user_prompt = self.build_user_prompt(transcript_data)
        combined_prompt = f"{system_prompt}\n\n{user_prompt}"

        response = self.provider.generate(
            combined_prompt,
            temperature=self.settings.temperature,
            max_tokens=self.settings.max_tokens,
            timeout=300,
        )

        json_result = self._extract_json(response.text)
        return self._ensure_schema(json_result, transcript_data)

    def _extract_json(self, text: str) -> Dict[str, Any]:
        if "```json" in text:
            start = text.find("```json") + 7
            end = text.find("```", start)
            text = text[start:end].strip()
        elif "```" in text:
            start = text.find("```") + 3
            end = text.find("```", start)
            text = text[start:end].strip()

        start_idx = text.find("{")
        end_idx = text.rfind("}") + 1
        if start_idx == -1 or end_idx == 0:
            raise ValueError(f"No JSON found in response: {text[:200]}")

        try:
            return json.loads(text[start_idx:end_idx])
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSON in response: {exc}\nFragment: {text[:500]}")

    def _ensure_schema(self, analysis: Dict[str, Any], transcript_data: Dict[str, Any]) -> Dict[str, Any]:
        updated = dict(analysis)
        if not isinstance(updated.get("utterance_states"), list):
            logger.warning("Ollama response missing 'utterance_states' – generating defaults")
            updated["utterance_states"] = self._build_default_states(transcript_data.get("utterances", []))

        if "ued_metrics" not in updated or not isinstance(updated["ued_metrics"], dict):
            logger.warning("Ollama response missing 'ued_metrics' – inserting empty metrics")
            updated["ued_metrics"] = {
                "home_base": {},
                "variability": {},
                "instability": {},
                "rise_rate": {},
                "recovery_rate": {},
            }

        if "marker_summary" not in updated or not isinstance(updated["marker_summary"], dict):
            logger.warning("Ollama response missing 'marker_summary' – inserting defaults")
            updated["marker_summary"] = {"frequencies": {}, "dominance_ranking": []}

        updated.setdefault("psychological_lenses", {})
        updated.setdefault("disclaimers", {})
        updated.setdefault("input_meta", transcript_data.get("transcript_meta", {}))
        return updated

    def _build_default_states(self, utterances: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        defaults: List[Dict[str, Any]] = []
        for idx, utt in enumerate(utterances):
            defaults.append(
                {
                    "id": utt.get("id", idx),
                    "speaker": utt.get("speaker", "Unknown"),
                    "order_index": idx,
                    "text": utt.get("text", ""),
                    "valence": 0.5,
                    "arousal": 0.5,
                    "dominance": 0.5,
                    "discrete_emotions": utt.get("prosody", {}).get("discrete_emotions", {}),
                    "confidence": 0.0,
                    "markers": [],
                }
            )
        return defaults

    def get_model_info(self) -> Dict[str, str]:
        """Expose settings for UI display."""
        return {
            "name": self.settings.model,
            "base_url": self.settings.base_url,
        }
