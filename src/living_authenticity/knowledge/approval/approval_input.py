"""Explicit approval input parsing: accepted values only."""
from .outcome import ACCEPTED_APPROVAL_INPUTS


def parse_approval_input(value) -> bool:
    """Return True only for an explicit accepted human input.

    Accepted (after strip().lower()): "y", "yes". Everything else --
    blank, "n", "no", invalid, timeout markers, None -- is rejection.
    Default is No. Raises TypeError for non-string input so callers
    cannot smuggle approval through unexpected types.
    """
    if not isinstance(value, str):
        raise TypeError("approval input must be a string")
    return value.strip().lower() in ACCEPTED_APPROVAL_INPUTS
