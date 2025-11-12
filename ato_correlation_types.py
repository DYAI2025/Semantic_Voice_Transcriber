from dataclasses import dataclass, field
from typing import Dict, List, Optional
import numpy as np

@dataclass
class ProsodyFeatureVector:
    """Vector representation of prosodic features for correlation."""
    pitch_deviation: float
    tempo_deviation: float
    energy_deviation: float
    pause_frequency: float
    pitch_variability: float

    def to_array(self) -> np.ndarray:
        """Convert to numpy array for calculations."""
        return np.array([
            self.pitch_deviation,
            self.tempo_deviation,
            self.energy_deviation,
            self.pause_frequency,
            self.pitch_variability
        ])

@dataclass
class MarkerCorrelation:
    """Statistical correlation between prosody and a marker."""
    marker_name: str
    confidence: float
    sample_count: int
    contributing_features: Dict[str, float]

    def is_confident(self, threshold: float = 0.5) -> bool:
        """Check if correlation meets confidence threshold."""
        return self.confidence >= threshold

@dataclass
class CorrelationModel:
    """Complete correlation model for a speaker."""
    speaker_id: str
    correlations: Dict[str, List[MarkerCorrelation]] = field(default_factory=dict)
    total_samples: int = 0