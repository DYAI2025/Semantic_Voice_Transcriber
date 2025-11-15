# psychoanalysis_pipeline.py
import yaml
import os
from pathlib import Path
from psychoanalysis_cache import CacheManager
from turnpoint_detector import TurnpointDetector
from psychoanalysis_api import PsychoanalysisAPI

class PsychoanalysisPipeline:
    """Main orchestrator for psychoanalysis pipeline: cache → API → turnpoints → output"""

    def __init__(self, config_path="config/psychoanalysis_config.yaml", cache_dir=None):
        """Initialize pipeline with config and components

        Args:
            config_path: Path to psychoanalysis config YAML
            cache_dir: Optional custom cache directory (defaults to config value)
        """
        # Load config
        with open(config_path) as f:
            self.config = yaml.safe_load(f)

        # Initialize cache manager
        if cache_dir:
            self.cache = CacheManager(cache_dir=cache_dir)
        else:
            self.cache = CacheManager(cache_dir=self.config["cache"]["directory"])

        # Initialize turnpoint detector
        self.turnpoint_detector = TurnpointDetector(config_path=config_path)

        # Initialize API client (only if API key exists)
        if os.environ.get("OPENAI_API_KEY"):
            self.api = PsychoanalysisAPI(config_path=config_path)
        else:
            self.api = None

    def analyze_transcript(self, transcript_data, skill_path):
        """Analyze transcript with caching, API call, and turnpoint detection

        Args:
            transcript_data: Dictionary with transcript_meta and utterances
            skill_path: Path to emotion-dynamics-deep-insight SKILL.md

        Returns:
            dict: Unified JSON with utterance_states, ued_metrics, marker_summary, turnpoints
        """
        # Step 1: Check cache
        cached_analysis = self.cache.get_cached_analysis(transcript_data)

        if cached_analysis:
            # Use cached analysis (skip API call)
            analysis = cached_analysis
        elif self.api:
            # Step 2: Call OpenAI API (cache miss)
            analysis = self.api.analyze_transcript(transcript_data, skill_path)

            # Step 3: Save to cache
            self.cache.save_analysis(transcript_data, analysis)
        else:
            # No cache and no API key - cannot proceed
            raise ValueError(
                "No cached analysis found and OPENAI_API_KEY not set. "
                "Cannot analyze transcript without API access."
            )

        # Step 4: Merge prosody data from transcript into utterance_states
        utterance_states_with_prosody = self._merge_prosody_data(
            transcript_data["utterances"],
            analysis["utterance_states"]
        )

        # Step 5: Detect turnpoints using tri-modal algorithm
        turnpoints = self.turnpoint_detector.detect_turnpoints(utterance_states_with_prosody)

        # Step 6: Return unified JSON
        return {
            "input_meta": analysis.get("input_meta", {}),
            "utterance_states": utterance_states_with_prosody,
            "ued_metrics": analysis["ued_metrics"],
            "marker_summary": analysis["marker_summary"],
            "turnpoints": turnpoints,
            "psychological_lenses": analysis.get("psychological_lenses", {}),
            "disclaimers": analysis.get("disclaimers", {})
        }

    def _merge_prosody_data(self, transcript_utterances, utterance_states):
        """Merge prosody data from transcript into utterance states

        Args:
            transcript_utterances: List of utterances from transcript_data
            utterance_states: List of utterance states from API analysis

        Returns:
            list: Utterance states with merged prosody and ued_emotions
        """
        # Create lookup dict by utterance ID
        prosody_by_id = {
            utt["id"]: utt.get("prosody", {})
            for utt in transcript_utterances
        }

        # Merge prosody into utterance states
        merged = []
        for state in utterance_states:
            utterance_id = state["id"]

            # Create merged utterance with ued_emotions and prosody
            merged_state = {
                "id": utterance_id,
                "speaker": state.get("speaker", "Unknown"),
                "text": state["text"],
                "ued_emotions": {
                    "valence": state["valence"],
                    "arousal": state["arousal"],
                    "dominance": state.get("dominance", 0.5),
                    "discrete_emotions": state.get("discrete_emotions", {}),
                    "confidence": state.get("confidence", 0.0)
                },
                "markers": state.get("markers", [])
            }

            # Add prosody if available
            if utterance_id in prosody_by_id:
                merged_state["prosody"] = prosody_by_id[utterance_id]

            merged.append(merged_state)

        return merged
