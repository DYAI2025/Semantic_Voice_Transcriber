# tests/test_psychoanalysis_config.py
import pytest
from pathlib import Path
import yaml

def test_config_file_exists():
    """Config file should exist in config/ directory"""
    config_path = Path(__file__).parent.parent / "config" / "psychoanalysis_config.yaml"
    assert config_path.exists(), f"Config file not found at {config_path}"

def test_config_has_required_sections():
    """Config must have openai, cache, privacy, turnpoints, markers, dashboard sections"""
    config_path = Path(__file__).parent.parent / "config" / "psychoanalysis_config.yaml"
    with open(config_path) as f:
        config = yaml.safe_load(f)

    assert "openai" in config
    assert "cache" in config
    assert "privacy" in config
    assert "turnpoints" in config
    assert "markers" in config
    assert "dashboard" in config

def test_openai_config_structure():
    """OpenAI config must have model, max_tokens, temperature"""
    config_path = Path(__file__).parent.parent / "config" / "psychoanalysis_config.yaml"
    with open(config_path) as f:
        config = yaml.safe_load(f)

    openai = config["openai"]
    assert "api_key" in openai
    assert "model" in openai
    assert openai["model"] == "gpt-4-turbo-preview"
    assert "max_tokens" in openai
    assert "temperature" in openai
