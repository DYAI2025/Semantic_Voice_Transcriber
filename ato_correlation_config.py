import yaml
from dataclasses import dataclass, field
from typing import Dict, List
from pathlib import Path

@dataclass
class CorrelationConfig:
    """Configuration for ATO-prosody correlation system."""
    min_confidence_threshold: float = 0.5
    feature_window_size: float = 5.0
    update_frequency: str = "after_each_transcript"
    max_model_size_mb: int = 10
    feature_weights: Dict[str, float] = field(default_factory=lambda: {
        "pitch_deviation": 1.0,
        "tempo_deviation": 1.2,
        "energy_deviation": 0.8,
        "pause_frequency": 1.5,
        "pitch_variability": 1.3
    })
    marker_groups: Dict[str, List[str]] = field(default_factory=lambda: {
        "anxiety_related": [
            "ATO_ANXIETY_HESITATION",
            "ATO_FEAR",
            "ATO_DEFENSIVENESS_SHIFT_MARKER"
        ],
        "tempo_related": [
            "ATO_TEMPO_FAST",
            "ATO_TEMPO_SLOW"
        ]
    })

    @classmethod
    def from_yaml(cls, path: str) -> "CorrelationConfig":
        """Load configuration from YAML file."""
        with open(path, 'r') as f:
            data = yaml.safe_load(f)

        settings = data.get("correlation_settings", {})
        return cls(
            min_confidence_threshold=settings.get("min_confidence_threshold", 0.5),
            feature_window_size=settings.get("feature_window_size", 5.0),
            update_frequency=settings.get("update_frequency", "after_each_transcript"),
            max_model_size_mb=settings.get("max_model_size_mb", 10),
            feature_weights=data.get("feature_weights", cls.__dataclass_fields__["feature_weights"].default_factory()),
            marker_groups=data.get("marker_groups", cls.__dataclass_fields__["marker_groups"].default_factory())
        )

    def get_marker_group(self, group_name: str) -> List[str]:
        """Get markers in a specific group."""
        return self.marker_groups.get(group_name, [])