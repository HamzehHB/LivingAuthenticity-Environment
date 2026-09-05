"""Central configuration loading for the LivingAuthenticity Environment.

All configuration files live in the ``Config`` directory, and this module
is the single place in the codebase that reads them.

Public API:

* ``load_paths(config_dir)`` — load and validate ``paths.yaml``.
* ``load_models(config_dir)`` — load and validate ``models.yaml``.
* ``ConfigError`` — raised when a configuration file is missing or invalid.

The module-level ``PATHS`` and ``MODELS`` objects hold the validated
configuration of the repository ``Config`` directory and are the values
consumed by the rest of the codebase.
"""

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent

CONFIG_DIR = ROOT / "Config"

PATHS_FILE = "paths.yaml"
MODELS_FILE = "models.yaml"

_PATHS_REQUIRED_KEYS = (
    "project.root",
    "data.root",
    "models.bge_m3",
    "vector_db.lancedb",
    "memory.root",
    "obsidian.vault",
    "zotero.library",
    "exports.root",
    "cache.root",
    "logs.root",
    "prompts.root",
)


class ConfigError(RuntimeError):
    """Raised when a configuration file is missing or invalid."""


def _load_yaml(path: Path) -> dict:

    if not path.is_file():
        raise ConfigError(
            f"Configuration file not found: {path}"
        )

    try:
        with path.open("r", encoding="utf-8") as file:
            data = yaml.safe_load(file)
    except (OSError, yaml.YAMLError) as exc:
        raise ConfigError(
            f"Could not read configuration file {path}: {exc}"
        ) from exc

    if not isinstance(data, dict):
        raise ConfigError(
            f"Configuration file {path} must contain a mapping at the top level."
        )

    return data


def _resolve(data: dict, dotted_key: str):

    value = data

    for part in dotted_key.split("."):
        if not isinstance(value, dict) or part not in value:
            return None
        value = value[part]

    return value


def _require_non_empty_strings(data: dict, dotted_keys, source: Path) -> None:

    for key in dotted_keys:
        value = _resolve(data, key)
        if not isinstance(value, str) or not value.strip():
            raise ConfigError(
                f"Invalid configuration in {source}: "
                f"'{key}' must be set to a non-empty string."
            )


def load_paths(config_dir: Path | str = CONFIG_DIR) -> dict:
    """Load and validate ``paths.yaml`` from ``config_dir``."""

    source = Path(config_dir) / PATHS_FILE
    data = _load_yaml(source)
    _require_non_empty_strings(data, _PATHS_REQUIRED_KEYS, source)

    return data


def load_models(config_dir: Path | str = CONFIG_DIR) -> dict:
    """Load and validate ``models.yaml`` from ``config_dir``."""

    source = Path(config_dir) / MODELS_FILE
    data = _load_yaml(source)

    embedding = data.get("embedding")
    if not isinstance(embedding, dict) or not isinstance(embedding.get("active"), str):
        raise ConfigError(
            f"Invalid configuration in {source}: "
            f"'embedding.active' must be a string."
        )

    active = embedding["active"]

    model = data.get(active)
    if not isinstance(model, dict):
        raise ConfigError(
            f"Invalid configuration in {source}: "
            f"no section found for the active embedding model '{active}'."
        )

    dimension = model.get("dimension")
    if not isinstance(dimension, int) or isinstance(dimension, bool) or dimension <= 0:
        raise ConfigError(
            f"Invalid configuration in {source}: "
            f"'{active}.dimension' must be a positive integer."
        )

    if not isinstance(model.get("normalize"), bool):
        raise ConfigError(
            f"Invalid configuration in {source}: "
            f"'{active}.normalize' must be a boolean."
        )

    batch_size = model.get("batch_size")
    if not isinstance(batch_size, int) or isinstance(batch_size, bool) or batch_size <= 0:
        raise ConfigError(
            f"Invalid configuration in {source}: "
            f"'{active}.batch_size' must be a positive integer."
        )

    return data


PATHS = load_paths()
MODELS = load_models()
