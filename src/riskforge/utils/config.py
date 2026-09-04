"""Configuration loader utility."""

import os
from pathlib import Path
from typing import Any, Dict
import yaml


def get_project_root() -> Path:
    """Returns the root directory of the Capstone project."""
    return Path(__file__).resolve().parents[3]


def load_config(config_name: str = "config.yaml") -> Dict[str, Any]:
    """Loads a YAML configuration file from the configs directory."""
    root = get_project_root()
    config_path = root / "configs" / config_name
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found at {config_path}")
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_cost_matrix() -> Dict[str, Any]:
    """Loads cost_matrix.yaml configuration."""
    return load_config("cost_matrix.yaml")
