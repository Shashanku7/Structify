"""
Config module for Structify.

Loads default settings from defaults.yaml so they can be used
throughout the project.
"""

import os
from pathlib import Path
import yaml

# Path to defaults.yaml (always relative to this file’s location)
CONFIG_PATH = Path(__file__).resolve().parent / "defaults.yaml"

def load_config() -> dict:
    """
    Load YAML configuration (defaults.yaml).

    Returns:
        dict: Parsed config dictionary
    """
    if not CONFIG_PATH.exists():
        raise FileNotFoundError(f"Config file not found at {CONFIG_PATH}")
    
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

# Load config at import time (so core modules can just `from structify.config import CONFIG`)
CONFIG = load_config()