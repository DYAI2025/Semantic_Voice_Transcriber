# turnpoint_detector.py
import yaml
from pathlib import Path

class TurnpointDetector:
    """Tri-modal turnpoint detection: emotion + markers + prosody"""

    def __init__(self, config_path="config/psychoanalysis_config.yaml"):
        """Initialize with config thresholds"""
        with open(config_path) as f:
            config = yaml.safe_load(f)

        tp_config = config["turnpoints"]
        self.valence_threshold = tp_config["valence_threshold"]
        self.arousal_threshold = tp_config["arousal_threshold"]
        self.prosody_pause_threshold = tp_config["prosody_pause_threshold_ms"]

    def detect_turnpoints(self, utterances):
        """Detect all turnpoints across utterances"""
        turnpoints = []

        for i in range(1, len(utterances)):
            curr = utterances[i]
            prev = utterances[i - 1]

            # 1. EMOTIONAL CHANGE POINT
            valence_jump = abs(curr["ued_emotions"]["valence"] - prev["ued_emotions"]["valence"])

            if valence_jump > self.valence_threshold:
                tp = {
                    "utterance_id": curr["id"],
                    "type": "emotional_shift",
                    "description": f"Valenzsprung: {prev['ued_emotions']['valence']:.2f} → {curr['ued_emotions']['valence']:.2f}",
                    "significance": "high" if valence_jump > 0.7 else "medium"
                }

                # PROSODY ENHANCEMENT
                if "prosody" in curr and curr["prosody"]["pause_before_ms"] > self.prosody_pause_threshold:
                    tp["significance"] = "high"
                    tp["prosody_support"] = f"Pause {curr['prosody']['pause_before_ms']}ms"

                turnpoints.append(tp)

            # 2. MARKER-BASED TURNPOINT: Resistance → Openness
            prev_has_resistance = any(m.startswith("ATO_RESISTANCE_") for m in prev["markers"])
            curr_has_resistance = any(m.startswith("ATO_RESISTANCE_") for m in curr["markers"])

            if prev_has_resistance and not curr_has_resistance and curr["ued_emotions"]["valence"] > 0:
                resistance_markers = [m for m in prev["markers"] if m.startswith("ATO_RESISTANCE_")]
                turnpoints.append({
                    "utterance_id": curr["id"],
                    "type": "resistance_breakthrough",
                    "description": "Widerstand aufgelöst, positive Valenz",
                    "markers_involved": resistance_markers,
                    "significance": "high"
                })

            # 3. MARKER-BASED TURNPOINT: Defense → Insight
            prev_has_defense = any(m.startswith("ATO_DEFENSE_") for m in prev["markers"])
            dominance_increase = curr["ued_emotions"].get("dominance", 0) - prev["ued_emotions"].get("dominance", 0)

            if prev_has_defense and dominance_increase > 0.2:
                defense_markers = [m for m in prev["markers"] if m.startswith("ATO_DEFENSE_")]
                turnpoints.append({
                    "utterance_id": curr["id"],
                    "type": "defensive_resolution",
                    "description": "Abwehrmechanismus reduziert, Dominanz gestiegen",
                    "markers_involved": defense_markers,
                    "significance": "medium"
                })

            # 4. NARRATIVE TURNPOINT: Theme change
            prev_themes = [m for m in prev["markers"] if m.startswith("ATO_THEME_")]
            curr_themes = [m for m in curr["markers"] if m.startswith("ATO_THEME_")]

            if prev_themes != curr_themes and len(curr_themes) > 0:
                turnpoints.append({
                    "utterance_id": curr["id"],
                    "type": "narrative_shift",
                    "description": f"Themenwechsel: {prev_themes} → {curr_themes}",
                    "significance": "medium"
                })

        return turnpoints
