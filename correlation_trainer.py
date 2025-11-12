import yaml
from pathlib import Path
from typing import List, Dict, Any
from ato_correlation_engine import CorrelationEngine
from ato_correlation_types import ProsodyFeatureVector, MarkerCorrelation

class CorrelationTrainer:
    """Trains correlation models from annotated transcripts."""

    def __init__(self, engine: CorrelationEngine):
        self.engine = engine

    def load_annotated_transcript(self, path: Path) -> Dict[str, Any]:
        """Load annotated transcript from YAML file."""
        with open(path, 'r') as f:
            return yaml.safe_load(f)

    def train_from_transcript(self, transcript_path: Path) -> List[MarkerCorrelation]:
        """Train correlations from a single annotated transcript."""
        data = self.load_annotated_transcript(transcript_path)
        segments = data.get("segments", [])

        if not segments:
            return []

        # Collect all unique markers
        all_markers = set()
        for segment in segments:
            all_markers.update(segment.get("markers", []))

        correlations = []

        # For each marker, calculate correlation
        for marker_name in all_markers:
            features = []
            presence = []

            for segment in segments:
                prosody = segment.get("prosody", {})
                feature_vec = ProsodyFeatureVector(
                    pitch_deviation=prosody.get("pitch_deviation", 0),
                    tempo_deviation=prosody.get("tempo_deviation", 0),
                    energy_deviation=prosody.get("energy_deviation", 0),
                    pause_frequency=prosody.get("pause_frequency", 0),
                    pitch_variability=prosody.get("pitch_variability", 0)
                )
                features.append(feature_vec)
                presence.append(marker_name in segment.get("markers", []))

            # Calculate correlation
            correlation = self.engine.calculate_correlation(
                marker_name,
                features,
                presence
            )

            # Update model
            self.engine.update_model(correlation)
            correlations.append(correlation)

        return correlations

    def train_from_directory(self, directory: Path) -> Dict[str, List[MarkerCorrelation]]:
        """Train from all annotated transcripts in a directory."""
        all_correlations = {}

        for yaml_file in directory.glob("*.yaml"):
            try:
                correlations = self.train_from_transcript(yaml_file)
                for corr in correlations:
                    if corr.marker_name not in all_correlations:
                        all_correlations[corr.marker_name] = []
                    all_correlations[corr.marker_name].append(corr)
            except Exception as e:
                print(f"Error training from {yaml_file}: {e}")
                continue

        return all_correlations