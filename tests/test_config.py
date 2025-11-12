import pytest
from pathlib import Path
from config.config_loader import ConfigLoader

def test_config_loader_loads_integration_config():
    """Test loading integration configuration"""
    loader = ConfigLoader()
    config = loader.load_integration_config()

    assert 'layers' in config
    assert 'display' in config
    assert 'performance' in config
    assert 'thresholds' in config

def test_config_has_correct_defaults():
    """Test configuration has sensible defaults"""
    loader = ConfigLoader()
    config = loader.load_integration_config()

    assert config['layers']['base_transcription'] == True
    assert config['display']['marker_mode'] == 'dual'
    assert config['performance']['quality_preset'] == 'balanced'