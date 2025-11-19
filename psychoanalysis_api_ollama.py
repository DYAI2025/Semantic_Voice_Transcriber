# psychoanalysis_api_ollama.py
"""
Ollama-based API for psychoanalytic analysis
100% free, runs locally, no API costs
"""

import json
import yaml
import requests
from pathlib import Path
from typing import Dict, Any


class OllamaPsychoanalysisAPI:
    """Ollama API client for psychoanalytic analysis - FREE and LOCAL"""

    def __init__(self, config_path="config/psychoanalysis_config.yaml"):
        """Initialize Ollama API client with configuration"""
        with open(config_path) as f:
            self.config = yaml.safe_load(f)

        # Ollama configuration
        self.base_url = self.config.get("ollama", {}).get("base_url", "http://localhost:11434")
        self.model = self.config.get("ollama", {}).get("model", "qwen2.5-coder:7b")
        self.temperature = self.config.get("ollama", {}).get("temperature", 0.7)
        self.max_tokens = self.config.get("ollama", {}).get("max_tokens", 4000)

        # Test connection
        self._test_connection()

    def _test_connection(self):
        """Test if Ollama is running"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code != 200:
                raise ConnectionError(f"Ollama not responding: {response.status_code}")

            # Check if model is available
            models = response.json().get("models", [])
            model_names = [m["name"] for m in models]

            if self.model not in model_names:
                print(f"⚠️ Model '{self.model}' not found. Available models: {model_names}")
                print(f"   Download with: ollama pull {self.model}")
                # Try to use first available model
                if model_names:
                    self.model = model_names[0]
                    print(f"   Using: {self.model}")

        except requests.exceptions.ConnectionError:
            raise ConnectionError(
                "❌ Ollama not running! Start with: ollama serve\n"
                "   Or install from: https://ollama.com/download"
            )

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

WICHTIG: Antworte NUR mit der strukturierten JSON-Ausgabe wie im Skill beschrieben.
KEINE zusätzlichen Erklärungen, KEIN Markdown, NUR das JSON-Objekt."""

        return system_prompt

    def build_user_prompt(self, transcript_data):
        """Build user prompt from transcript JSON"""
        user_prompt = f"""Analysiere folgendes Transkript:

**Metadaten:**
- Datei: {transcript_data['transcript_meta']['file']}
- Sprecher: {', '.join(transcript_data['transcript_meta']['speaker_labels'])}
- Dauer: {transcript_data['transcript_meta']['duration_seconds']}s

**Utterances:**
{json.dumps(transcript_data['utterances'], indent=2, ensure_ascii=False)}

Führe die vollständige Analyse durch und gib das Ergebnis im spezifizierten JSON-Format zurück.
Antworte NUR mit dem JSON-Objekt, keine weiteren Texte."""

        return user_prompt

    def analyze_transcript(self, transcript_data: Dict[str, Any], skill_path: str) -> Dict[str, Any]:
        """
        Analyze transcript using Ollama

        Args:
            transcript_data: Transcript data with utterances
            skill_path: Path to emotion-dynamics SKILL.md

        Returns:
            Analysis results as dict
        """
        system_prompt = self.build_system_prompt(skill_path)
        user_prompt = self.build_user_prompt(transcript_data)

        # Combine prompts for Ollama
        full_prompt = f"{system_prompt}\n\n{user_prompt}"

        # Call Ollama API
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": full_prompt,
                    "stream": False,
                    "options": {
                        "temperature": self.temperature,
                        "num_predict": self.max_tokens,
                    }
                },
                timeout=300  # 5 minutes max
            )

            if response.status_code != 200:
                raise RuntimeError(f"Ollama error: {response.status_code} - {response.text}")

            result = response.json()
            response_text = result.get("response", "")

            # Extract JSON from response
            json_result = self._extract_json(response_text)

            return json_result

        except requests.exceptions.Timeout:
            raise TimeoutError("Ollama request timed out after 5 minutes")
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Ollama connection failed: {e}")

    def _extract_json(self, text: str) -> Dict[str, Any]:
        """Extract JSON object from potentially messy response"""
        # Try to find JSON in markdown code blocks
        if "```json" in text:
            start = text.find("```json") + 7
            end = text.find("```", start)
            text = text[start:end].strip()
        elif "```" in text:
            start = text.find("```") + 3
            end = text.find("```", start)
            text = text[start:end].strip()

        # Find first { and last }
        start_idx = text.find("{")
        end_idx = text.rfind("}") + 1

        if start_idx == -1 or end_idx == 0:
            raise ValueError(f"No JSON found in response: {text[:200]}")

        json_text = text[start_idx:end_idx]

        try:
            return json.loads(json_text)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in response: {e}\n\nText: {json_text[:500]}")

    def get_model_info(self) -> Dict[str, str]:
        """Get information about current model"""
        try:
            response = requests.get(f"{self.base_url}/api/tags")
            models = response.json().get("models", [])
            for model in models:
                if model["name"] == self.model:
                    return {
                        "name": model["name"],
                        "size": model.get("size", "unknown"),
                        "modified": model.get("modified_at", "unknown")
                    }
        except:
            pass

        return {"name": self.model, "size": "unknown", "modified": "unknown"}


# Standalone test
if __name__ == "__main__":
    print("Testing Ollama Psychoanalysis API...\n")

    try:
        api = OllamaPsychoanalysisAPI()

        print(f"✅ Connected to Ollama")
        print(f"   Model: {api.model}")
        print(f"   Base URL: {api.base_url}")

        info = api.get_model_info()
        print(f"   Size: {info['size']}")
        print(f"   Modified: {info['modified']}")

        # Test with simple data
        test_data = {
            "transcript_meta": {
                "file": "test.m4a",
                "speaker_labels": ["Patient", "Therapeut"],
                "duration_seconds": 120
            },
            "utterances": [
                {
                    "id": 0,
                    "speaker": "Patient",
                    "text": "Ich fühle mich heute sehr traurig.",
                    "start": 0.0,
                    "end": 3.0
                },
                {
                    "id": 1,
                    "speaker": "Therapeut",
                    "text": "Können Sie mir mehr darüber erzählen?",
                    "start": 3.5,
                    "end": 5.5
                }
            ]
        }

        skill_path = Path("emotion_dynaminc-skill/SKILL.md")
        if skill_path.exists():
            print("\n🔍 Testing analysis...")
            result = api.analyze_transcript(test_data, skill_path)
            print(f"✅ Analysis complete!")
            print(f"   Keys: {list(result.keys())}")
        else:
            print(f"\n⚠️ Skill file not found: {skill_path}")
            print("   Skipping analysis test")

    except Exception as e:
        print(f"❌ Error: {e}")
