"""Configuration loader for the news site."""
import os
from pathlib import Path
from typing import Any, Dict, Optional

import yaml

from core.exceptions import ConfigurationError

_config: Optional[Dict[str, Any]] = None


def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Load configuration from YAML file.

    Args:
        config_path: Path to config file. Defaults to config.yaml in project root.

    Returns:
        Configuration dictionary

    Raises:
        ConfigurationError: If config file not found or invalid
    """
    global _config

    if config_path is None:
        # Look for config.yaml in project root
        project_root = Path(__file__).parent.parent.parent.parent
        config_path = project_root / "config.yaml"

        # Fall back to example config if main config doesn't exist
        if not config_path.exists():
            config_path = project_root / "config.example.yaml"

    config_path = Path(config_path)

    if not config_path.exists():
        raise ConfigurationError(f"Config file not found: {config_path}")

    try:
        with open(config_path, "r") as f:
            _config = yaml.safe_load(f)
    except yaml.YAMLError as e:
        raise ConfigurationError(f"Invalid YAML in config file: {e}")

    return _config


def get_config() -> Dict[str, Any]:
    """
    Get loaded configuration.

    Returns:
        Configuration dictionary

    Raises:
        ConfigurationError: If config not loaded
    """
    global _config

    if _config is None:
        _config = load_config()

    return _config
