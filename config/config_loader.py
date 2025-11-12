import yaml
from pathlib import Path
from typing import Dict, Any

class ConfigLoader:
    """Loader for integration configuration"""

    def __init__(self, config_dir: Path = None):
        """Initialize config loader

        Args:
            config_dir: Directory containing config files
        """
        if config_dir is None:
            config_dir = Path(__file__).parent
        self.config_dir = Path(config_dir)
        self.integration_config_path = self.config_dir / 'integration_config.yaml'

    def load_integration_config(self) -> Dict[str, Any]:
        """Load integration configuration

        Returns:
            Configuration dictionary
        """
        if not self.integration_config_path.exists():
            return self.get_default_config()

        try:
            with open(self.integration_config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                return self.validate_config(config)
        except Exception as e:
            print(f"Error loading config: {e}")
            return self.get_default_config()

    def get_default_config(self) -> Dict[str, Any]:
        """Get default configuration

        Returns:
            Default configuration dictionary
        """
        return {
            'layers': {
                'base_transcription': True,
                'turning_points': False,
                'enhanced_speakers': True
            },
            'display': {
                'marker_mode': 'dual',
                'speaker_colors': True,
                'turning_point_highlights': True,
                'confidence_threshold': 0.7
            },
            'performance': {
                'quality_preset': 'balanced',
                'parallel_processing': True,
                'cache_embeddings': True,
                'batch_size': 32
            },
            'thresholds': {
                'tempo_threshold': 20.0,
                'pitch_threshold': 15.0,
                'energy_threshold': 25.0,
                'pause_threshold_ms': 1000,
                'turning_point_confidence': 0.7,
                'cosd_peak_threshold': 0.6,
                'speaker_confidence': 0.85
            }
        }

    def validate_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and fill missing values in config

        Args:
            config: Configuration dictionary to validate

        Returns:
            Validated configuration with defaults for missing values
        """
        default = self.get_default_config()

        # Merge with defaults for missing keys
        for key in default:
            if key not in config:
                config[key] = default[key]
            elif isinstance(default[key], dict):
                for subkey in default[key]:
                    if subkey not in config[key]:
                        config[key][subkey] = default[key][subkey]

        return config

    def save_config(self, config: Dict[str, Any]):
        """Save configuration to file

        Args:
            config: Configuration dictionary to save
        """
        with open(self.integration_config_path, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, default_flow_style=False, allow_unicode=True)

    def update_config(self, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update configuration with new values

        Args:
            updates: Dictionary of updates to apply

        Returns:
            Updated configuration
        """
        config = self.load_integration_config()

        # Deep update
        for key, value in updates.items():
            if key in config:
                if isinstance(value, dict) and isinstance(config[key], dict):
                    config[key].update(value)
                else:
                    config[key] = value
            else:
                config[key] = value

        self.save_config(config)
        return config