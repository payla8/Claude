"""Configuration loader for trading bot"""

import yaml
import os
from pathlib import Path
from typing import Dict, Any
from dotenv import load_dotenv


class ConfigLoader:
    """Load and manage configuration"""

    def __init__(self, config_path: str = "config.yaml"):
        self.config_path = Path(config_path)
        load_dotenv()
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_path}")

        with open(self.config_path, 'r') as f:
            config = yaml.safe_load(f)

        # Override with environment variables
        config['trading']['mode'] = os.getenv('TRADING_MODE', config['trading']['mode'])

        return config

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key (supports dot notation)"""
        keys = key.split('.')
        value = self.config

        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default

        return value if value is not None else default

    def get_all(self) -> Dict[str, Any]:
        """Get all configuration"""
        return self.config.copy()


# Global config instance
_config_instance = None


def get_config() -> ConfigLoader:
    """Get global config instance"""
    global _config_instance
    if _config_instance is None:
        _config_instance = ConfigLoader()
    return _config_instance
