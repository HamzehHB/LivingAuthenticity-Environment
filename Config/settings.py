from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parent.parent

CONFIG_DIR = ROOT / "Config"

with open(CONFIG_DIR / "paths.yaml", "r", encoding="utf-8") as f:
    PATHS = yaml.safe_load(f)

with open(CONFIG_DIR / "models.yaml", "r", encoding="utf-8") as f:
    MODELS = yaml.safe_load(f)
