"""Sensitive-data detection utilities (reusable).

Detection is value-safe: functions report **which** known pattern matched,
never the surrounding secret value. Callers must not log matched content.
"""

from pathlib import Path

import yaml

SECRET_PATTERNS = (
    "AKIA",                        # AWS access key id prefix
    "ghp_",                        # GitHub personal access token
    "github_pat_",                 # GitHub fine-grained token
    "xoxb",                        # Slack bot token
    "xoxp",                        # Slack user token
    "xoxa",                        # Slack workspace/app token
    "BEGIN RSA PRIVATE KEY",
    "BEGIN OPENSSH PRIVATE KEY",
    "BEGIN EC PRIVATE KEY",
    "BEGIN PRIVATE KEY",
)

_CONFIG_FILE = (
    Path(__file__).resolve().parent.parent.parent.parent
    / "Config" / "paths.local.yaml"
)


def _load_machine_specific_path_prefixes() -> tuple[str, ...]:
    """Load machine-specific path prefixes from the local-only config.

    Returns an empty tuple when the local config is absent, malformed, or
    does not define any prefixes, so a fresh clone detects nothing and
    never exposes a real path in tracked code.
    """

    if not _CONFIG_FILE.is_file():
        return ()
    try:
        with _CONFIG_FILE.open("r", encoding="utf-8") as file:
            data = yaml.safe_load(file)
    except (OSError, yaml.YAMLError):
        return ()
    if not isinstance(data, dict):
        return ()
    prefixes = data.get("machine_specific_path_prefixes")
    if not isinstance(prefixes, (list, tuple)):
        return ()
    return tuple(str(prefix) for prefix in prefixes)


# Loaded once at import time from the gitignored local config. This is a
# module-level attribute so tests can monkeypatch it directly.
MACHINE_SPECIFIC_PATH_PREFIXES = _load_machine_specific_path_prefixes()


def find_secrets(text: str) -> tuple[str, ...]:
    """Return the labels of secret patterns present in ``text``."""

    return tuple(pattern for pattern in SECRET_PATTERNS if pattern in text)


def contains_secret(text: str) -> bool:
    """Return ``True`` when ``text`` matches a known secret pattern."""

    return any(pattern in text for pattern in SECRET_PATTERNS)


def contains_machine_specific_path(text: str) -> bool:
    """Return ``True`` when ``text`` contains a machine-specific path."""

    return any(prefix in text for prefix in MACHINE_SPECIFIC_PATH_PREFIXES)
