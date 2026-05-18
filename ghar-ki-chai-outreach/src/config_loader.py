"""Helpers for loading YAML configuration and environment variables."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CONFIG_DIR = PROJECT_ROOT / "config"


def load_environment() -> None:
    """Load local .env values if the user has created a .env file."""
    load_dotenv(PROJECT_ROOT / ".env")


def load_yaml_config(file_name: str) -> dict[str, Any]:
    """Load a YAML config file from the config directory."""
    config_path = CONFIG_DIR / file_name
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with config_path.open("r", encoding="utf-8") as file:
        data = yaml.safe_load(file) or {}

    if not isinstance(data, dict):
        raise ValueError(f"Expected {config_path} to contain a YAML mapping.")

    return data
