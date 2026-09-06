"""Path boundary enforcement (default-deny) for the LivingAuthenticity
Environment.

This is runtime security infrastructure for upcoming checkpoints: ingestion
input validation, execution-target validation, and audit-path validation.

Policy:

* Nothing is allowed unless an allowed root was explicitly configured.
* A path is accepted only when it resolves inside (or equals) one of the
  allowed roots. Resolution normalizes traversal and follows symlinks.
* The production persistent-data root must never be configured by
  development code. Runtime components receive their allowed roots from the
  governed configuration (``Config/paths.local.yaml`` via
  ``Config/settings.py``).
"""

import os
from pathlib import Path


class PathOutsideBoundaryError(Exception):
    """Raised when a path resolves outside every allowed root."""


class PathBoundary:
    """A default-deny path boundary.

    With no roots configured, every path is rejected. Paths are compared
    after full resolution and case normalization, so traversal segments and
    sibling directories with a shared name prefix cannot slip through.
    """

    def __init__(self, *roots):
        self._roots = tuple(self._normalized(root) for root in roots)

    def validate(self, path):
        """Return the resolved ``path`` if it is inside the boundary.

        Raises :class:`PathOutsideBoundaryError` otherwise.
        """

        resolved = self._normalized(path)

        for root in self._roots:
            if resolved == root or root in resolved.parents:
                return Path(path).expanduser().resolve()

        raise PathOutsideBoundaryError(
            f"path is outside every allowed boundary: {resolved}"
        )

    def is_allowed(self, path) -> bool:
        """Return ``True`` when ``path`` resolves inside the boundary."""

        try:
            self.validate(path)
        except PathOutsideBoundaryError:
            return False
        return True

    @staticmethod
    def _normalized(path) -> Path:
        resolved = Path(path).expanduser().resolve()
        return Path(os.path.normcase(str(resolved)))
