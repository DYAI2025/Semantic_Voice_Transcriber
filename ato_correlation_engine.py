import numpy as np
from typing import List, Optional
from dataclasses import dataclass
from ato_correlation_types import (
    ProsodyFeatureVector,
    MarkerCorrelation,
    CorrelationModel
)
from ato_correlation_config import CorrelationConfig

class CorrelationEngine:
    """Engine for learning and applying ATO-prosody correlations."""

    def __init__(self, speaker_id: str, config: Optional[CorrelationConfig] = None):
        self.speaker_id = speaker_id
        self.config = config or CorrelationConfig()
        self.model = CorrelationModel(speaker_id=speaker_id)

    def calculate_correlation(
        self,
        marker_name: str,
        features: List[ProsodyFeatureVector],
        marker_presence: List[bool]
    ) -> MarkerCorrelation:
        """Calculate correlation between prosody features and marker presence."""
        if len(features) != len(marker_presence):
            raise ValueError("Features and marker presence lists must have same length")

        # Convert to arrays
        feature_matrix = np.array([f.to_array() for f in features])
        presence_array = np.array(marker_presence, dtype=float)

        # Calculate weighted correlations
        correlations = {}
        for idx, feature_name in enumerate([
            "pitch_deviation", "tempo_deviation", "energy_deviation",
            "pause_frequency", "pitch_variability"
        ]):
            feature_col = feature_matrix[:, idx]
            # Simple correlation coefficient
            if np.std(feature_col) > 0 and np.std(presence_array) > 0:
                corr = np.corrcoef(feature_col, presence_array)[0, 1]
                weight = self.config.feature_weights.get(feature_name, 1.0)
                correlations[feature_name] = abs(corr) * weight
            else:
                correlations[feature_name] = 0.0

        # Overall confidence is weighted average (capped at 1.0)
        confidence = min(np.mean(list(correlations.values())), 1.0)

        return MarkerCorrelation(
            marker_name=marker_name,
            confidence=confidence,
            sample_count=len(features),
            contributing_features=correlations
        )

    def predict_markers(
        self,
        features: ProsodyFeatureVector,
        threshold: float = 0.5
    ) -> List[MarkerCorrelation]:
        """Predict which markers should apply based on prosody features."""
        predictions = []

        for marker_name, correlations in self.model.correlations.items():
            # Use most recent correlation
            if correlations:
                latest = correlations[-1]
                if latest.is_confident(threshold):
                    # Calculate match score based on contributing features
                    feature_array = features.to_array()
                    feature_names = [
                        "pitch_deviation", "tempo_deviation", "energy_deviation",
                        "pause_frequency", "pitch_variability"
                    ]

                    match_score = 0
                    for idx, fname in enumerate(feature_names):
                        if fname in latest.contributing_features:
                            # Higher feature value + high contribution = higher match
                            match_score += abs(feature_array[idx]) * latest.contributing_features[fname]

                    # Normalize match score
                    if match_score > 0:
                        match_confidence = min(latest.confidence * (match_score / len(feature_names)), 1.0)

                        if match_confidence >= threshold:
                            predictions.append(MarkerCorrelation(
                                marker_name=marker_name,
                                confidence=match_confidence,
                                sample_count=latest.sample_count,
                                contributing_features=latest.contributing_features
                            ))

        return predictions

    def update_model(self, correlation: MarkerCorrelation) -> None:
        """Add new correlation to model."""
        if correlation.marker_name not in self.model.correlations:
            self.model.correlations[correlation.marker_name] = []

        self.model.correlations[correlation.marker_name].append(correlation)
        self.model.total_samples += correlation.sample_count