# psychoanalysis_api.py
import os
import yaml
from pathlib import Path
from openai import OpenAI
import json

class PsychoanalysisAPI:
    """OpenAI API client for psychoanalytic analysis using emotion-dynamics skill"""

    def __init__(self, config_path="config/psychoanalysis_config.yaml"):
        """Initialize API client with configuration"""
        with open(config_path) as f:
            self.config = yaml.safe_load(f)

        # Get API key from environment
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")

        self.client = OpenAI(api_key=api_key)
        self.model = self.config["openai"]["model"]
        self.max_tokens = self.config["openai"]["max_tokens"]
        self.temperature = self.config["openai"]["temperature"]

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

    def analyze_transcript(self, transcript_data, skill_path):
        """Send transcript to OpenAI API and return analysis"""
        system_prompt = self.build_system_prompt(skill_path)
        user_prompt = self.build_user_prompt(transcript_data)
        function_schema = self.build_function_schema()

        response = self.client.chat.completions.create(
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

        # Extract function call result
        function_call = response.choices[0].message.function_call
        analysis = json.loads(function_call.arguments)

        return analysis
