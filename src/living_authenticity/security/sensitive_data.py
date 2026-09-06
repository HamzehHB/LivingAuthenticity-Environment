"""Sensitive-data detection utilities (reusable).

Detection is value-safe: functions report **which** known pattern matched,
never the surrounding secret value. Callers must not log matched content.
"""

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

MACHINE_SPECIFIC_PATH_PREFIXES = (
    "F:/LivingAuthenticity_Data",
    "F:\\LivingAuthenticity_Data",
    "E:/LivingAuthenticity_AI",
    "E:\\LivingAuthenticity_AI",
)


def find_secrets(text: str) -> tuple[str, ...]:
    """Return the labels of secret patterns present in ``text``."""

    return tuple(pattern for pattern in SECRET_PATTERNS if pattern in text)


def contains_secret(text: str) -> bool:
    """Return ``True`` when ``text`` matches a known secret pattern."""

    return any(pattern in text for pattern in SECRET_PATTERNS)


def contains_machine_specific_path(text: str) -> bool:
    """Return ``True`` when ``text`` contains a machine-specific path."""

    return any(prefix in text for prefix in MACHINE_SPECIFIC_PATH_PREFIXES)
