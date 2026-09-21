"""Authoritative schema version read (no execution, no schema system)."""
from pathlib import Path

_SCHEMA_PATH = Path(__file__).resolve().parents[4] / "Knowledge-Schema.yaml"


def current_schema_version(schema_path=None) -> str:
    """Return the authoritative ``schema.version`` from Knowledge-Schema.yaml.

    Uses ``yaml.safe_load`` only. Returns "" when the file is missing,
    malformed, or declares no usable version string, so callers must
    treat an unverifiable version conservatively (fail closed on any
    explicit asserted version).
    """
    path = Path(schema_path) if schema_path is not None else _SCHEMA_PATH
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, ValueError):
        return ""
    try:
        import yaml
        data = yaml.safe_load(text)
    except Exception:
        return ""
    if not isinstance(data, dict):
        return ""
    schema = data.get("schema")
    if not isinstance(schema, dict):
        return ""
    version = schema.get("version")
    if not isinstance(version, str):
        return ""
    return version.strip()
