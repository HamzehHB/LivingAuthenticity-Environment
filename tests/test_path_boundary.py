import pytest

from src.living_authenticity.security import (
    PathBoundary,
    PathOutsideBoundaryError,
)


def test_default_deny_when_no_roots_configured(tmp_path):
    boundary = PathBoundary()

    assert boundary.is_allowed(tmp_path) is False
    with pytest.raises(PathOutsideBoundaryError):
        boundary.validate(tmp_path)


def test_path_inside_allowed_root_is_accepted(tmp_path):
    root = tmp_path / "vault"
    root.mkdir()
    target = root / "notes" / "note.md"
    target.parent.mkdir()

    boundary = PathBoundary(root)

    assert boundary.is_allowed(target) is True
    assert boundary.validate(target) == target.resolve()


def test_allowed_root_itself_is_accepted(tmp_path):
    boundary = PathBoundary(tmp_path)

    assert boundary.is_allowed(tmp_path) is True


def test_path_outside_allowed_root_is_rejected(tmp_path):
    allowed = tmp_path / "allowed"
    allowed.mkdir()
    outside = tmp_path / "outside" / "note.md"

    boundary = PathBoundary(allowed)

    assert boundary.is_allowed(outside) is False
    with pytest.raises(PathOutsideBoundaryError):
        boundary.validate(outside)


def test_sibling_directory_with_shared_name_prefix_is_rejected(tmp_path):
    allowed = tmp_path / "data"
    allowed.mkdir()
    sibling = tmp_path / "database" / "file.db"

    boundary = PathBoundary(allowed)

    assert boundary.is_allowed(sibling) is False


def test_traversal_is_resolved_and_rejected(tmp_path):
    allowed = tmp_path / "allowed"
    allowed.mkdir()
    secret = tmp_path / "secret.txt"
    secret.write_text("x", encoding="utf-8")
    traversal = allowed / ".." / "secret.txt"

    boundary = PathBoundary(allowed)

    assert boundary.is_allowed(traversal) is False


def test_string_paths_are_accepted(tmp_path):
    boundary = PathBoundary(str(tmp_path))

    assert boundary.is_allowed(str(tmp_path / "note.md")) is True
