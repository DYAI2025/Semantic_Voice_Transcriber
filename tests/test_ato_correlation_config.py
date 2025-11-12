import pytest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from ato_correlation_config import CorrelationConfig

def test_load_default_config():
    """Test loading default correlation configuration."""
    config = CorrelationConfig()
    assert config.min_confidence_threshold == 0.5
    assert config.feature_window_size == 5.0
    assert "pitch_deviation" in config.feature_weights

def test_load_config_from_yaml():
    """Test loading configuration from YAML file."""
    config = CorrelationConfig.from_yaml("correlation_config.yaml")
    assert config.min_confidence_threshold >= 0.0
    assert config.feature_window_size > 0
    assert len(config.marker_groups) > 0

def test_get_marker_group():
    """Test retrieving markers by group."""
    config = CorrelationConfig()
    anxiety_markers = config.get_marker_group("anxiety_related")
    assert "ATO_ANXIETY_HESITATION" in anxiety_markers