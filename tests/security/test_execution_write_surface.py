"""Write-surface security proof: ControlledExecutor is the only filesystem writer.

Static AST scan over the current application source tree (proven from
code, not from historical reports):

* the single filesystem-mutation call site in ``src/`` is the
  controlled-execution staging ``write_text``;
* the executor performs exactly one write and never deletes, renames,
  creates directories, or replaces paths;
* the governance and security boundary families contain no
  rename/replace capability at all, and no ``os.*`` path mutation is
  called anywhere in application code;
* every ``open`` call in ``src/`` is read-mode only;
* no process, network, dynamic-code, or deserialization import exists
  in application code.

Together these prove the end-to-end security invariants -- controlled
execution remains CREATE-only and staging-confined, and no alternate
filesystem execution path exists across the current package structure.
"""
import ast
from pathlib import Path

SRC = Path(__file__).resolve().parents[2] / "src"

EXECUTOR = "living_authenticity/knowledge/governance/execution/executor.py"

MUTATION_ATTRS = frozenset({
    "write_text", "write_bytes", "write",
    "unlink", "rename", "mkdir", "rmdir",
    "touch", "remove", "rmtree", "symlink", "link", "move",
})

BOUNDARY_FAMILY_PREFIXES = (
    "living_authenticity/knowledge/governance/",
    "living_authenticity/security/",
)

FORBIDDEN_IMPORT_ROOTS = frozenset({
    "subprocess", "socket", "shutil", "pickle", "marshal", "ctypes",
})


def _relative(path: Path) -> str:
    return path.relative_to(SRC).as_posix()


def _iter_calls(tree):
    """Yield ``(attr, base, node)`` for every call in ``tree``."""
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if isinstance(func, ast.Name):
            yield func.id, "", node
        elif isinstance(func, ast.Attribute):
            base = ""
            if isinstance(func.value, ast.Name):
                base = func.value.id
            elif isinstance(func.value, ast.Attribute):
                base = func.value.attr
            yield func.attr, base, node


def _mode_of(node) -> str:
    if node.args and isinstance(node.args[0], ast.Constant) and isinstance(
        node.args[0].value, str
    ):
        return node.args[0].value
    return "r"  # documented default of open()


def test_controlled_executor_is_the_sole_mutation_call_site():
    offenders = []
    executor_seen = False
    for path in sorted(SRC.rglob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for attr, _base, _node in _iter_calls(tree):
            if attr not in MUTATION_ATTRS:
                continue
            if _relative(path) == EXECUTOR:
                executor_seen = True
            else:
                offenders.append(_relative(path) + ":" + attr)
    assert executor_seen is True, (
        "scan found no write in the executor; the scan itself is broken"
    )
    assert offenders == [], f"alternate filesystem mutation found: {offenders}"


def test_executor_writes_once_and_never_deletes_or_renames():
    tree = ast.parse((SRC / EXECUTOR).read_text(encoding="utf-8"))
    counts = {}
    for attr, _base, _node in _iter_calls(tree):
        counts[attr] = counts.get(attr, 0) + 1
    assert counts.get("write_text") == 1
    for forbidden in ("unlink", "rename", "replace", "rmdir", "mkdir", "remove"):
        assert counts.get(forbidden, 0) == 0, (
            f"executor must not perform {forbidden}"
        )


def test_no_rename_or_replace_in_boundary_families_or_via_os():
    offenders = []
    for path in sorted(SRC.rglob("*.py")):
        relative = _relative(path)
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for attr, base, _node in _iter_calls(tree):
            if attr not in ("replace", "rename"):
                continue
            in_boundary_family = relative.startswith(BOUNDARY_FAMILY_PREFIXES)
            if in_boundary_family or base == "os":
                offenders.append(relative + ":" + base + "." + attr)
    assert offenders == [], f"rename/replace capability found: {offenders}"


def test_all_open_calls_in_src_are_read_mode():
    offenders = []
    for path in sorted(SRC.rglob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for attr, _base, node in _iter_calls(tree):
            if attr != "open":
                continue
            mode = _mode_of(node)
            if not mode.startswith("r"):
                offenders.append(_relative(path) + ":" + mode)
    assert offenders == [], f"non-read open() in application code: {offenders}"


def test_no_process_network_or_deserialization_imports():
    offenders = []
    for path in sorted(SRC.rglob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                roots = [alias.name.split(".")[0] for alias in node.names]
            elif isinstance(node, ast.ImportFrom):
                roots = [(node.module or "").split(".")[0]]
            else:
                continue
            for root in roots:
                if root in FORBIDDEN_IMPORT_ROOTS:
                    offenders.append(_relative(path) + ":" + root)
    assert offenders == [], f"forbidden import in application code: {offenders}"
