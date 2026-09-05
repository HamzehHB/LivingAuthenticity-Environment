from pathlib import Path

import pytest

from Config import settings
from Config.settings import ConfigError, load_models, load_paths


VALID_PATHS_YAML = """
project:
  root: "D:/repo-root"
data:
  root: "D:/data-root"
models:
  bge_m3: "D:/data-root/Models/BGE_M3"
vector_db:
  lancedb: "D:/data-root/Database/Vector_Database"
memory:
  root: "D:/data-root/Memory"
obsidian:
  vault: "D:/data-root/Knowledge/Obsidian"
zotero:
  library: "D:/data-root/Knowledge/Zotero"
exports:
  root: "D:/data-root/Knowledge/Exports"
cache:
  root: "D:/data-root/Database/Cache"
logs:
  root: "D:/repo-root/Logs"
prompts:
  root: "D:/repo-root/Prompts"
"""

VALID_MODELS_YAML = """
embedding:
  active: "bge_m3"
bge_m3:
  dimension: 1024
  normalize: true
  batch_size: 16
"""


def _write(directory: Path, name: str, content: str) -> Path:
    path = directory / name
    path.write_text(content, encoding="utf-8")
    return path


def test_load_paths_returns_valid_configuration(tmp_path):
    _write(tmp_path, "paths.yaml", VALID_PATHS_YAML)

    paths = load_paths(tmp_path)

    assert paths["data"]["root"] == "D:/data-root"
    assert paths["vector_db"]["lancedb"] == "D:/data-root/Database/Vector_Database"


def test_load_paths_missing_file_raises_clear_error(tmp_path):
    with pytest.raises(ConfigError, match="not found"):
        load_paths(tmp_path)


def test_load_paths_missing_required_key_raises_clear_error(tmp_path):
    content = VALID_PATHS_YAML.replace('  root: "D:/data-root"', '  root: ""', 1)

    _write(tmp_path, "paths.yaml", content)

    with pytest.raises(ConfigError, match="'data.root'"):
        load_paths(tmp_path)


def test_load_paths_invalid_yaml_raises_clear_error(tmp_path):
    _write(tmp_path, "paths.yaml", "data: [unclosed")

    with pytest.raises(ConfigError, match="Could not read"):
        load_paths(tmp_path)


def test_load_paths_non_mapping_content_raises_clear_error(tmp_path):
    _write(tmp_path, "paths.yaml", "- just\n- a list\n")

    with pytest.raises(ConfigError, match="mapping"):
        load_paths(tmp_path)


def test_load_models_returns_valid_configuration(tmp_path):
    _write(tmp_path, "models.yaml", VALID_MODELS_YAML)

    models = load_models(tmp_path)

    assert models["embedding"]["active"] == "bge_m3"
    assert models["bge_m3"]["dimension"] == 1024


def test_load_models_missing_active_model_section_raises_clear_error(tmp_path):
    content = VALID_MODELS_YAML.replace("bge_m3:", "other_model:")

    _write(tmp_path, "models.yaml", content)

    with pytest.raises(ConfigError, match="'bge_m3'"):
        load_models(tmp_path)


def test_load_models_invalid_dimension_raises_clear_error(tmp_path):
    content = VALID_MODELS_YAML.replace("dimension: 1024", "dimension: 0")

    _write(tmp_path, "models.yaml", content)

    with pytest.raises(ConfigError, match="dimension"):
        load_models(tmp_path)


def test_load_models_non_boolean_normalize_raises_clear_error(tmp_path):
    content = VALID_MODELS_YAML.replace("normalize: true", 'normalize: "true"')

    _write(tmp_path, "models.yaml", content)

    with pytest.raises(ConfigError, match="normalize"):
        load_models(tmp_path)


def test_load_models_invalid_batch_size_raises_clear_error(tmp_path):
    content = VALID_MODELS_YAML.replace("batch_size: 16", "batch_size: 0")

    _write(tmp_path, "models.yaml", content)

    with pytest.raises(ConfigError, match="batch_size"):
        load_models(tmp_path)


def test_repository_configuration_loads_successfully():
    assert "vector_db" in settings.PATHS
    assert settings.MODELS["embedding"]["active"] == "bge_m3"
