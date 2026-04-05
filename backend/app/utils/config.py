import json
import logging
import os
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

from ..models.settings import AppSettings
from .encryption import encrypt_value, decrypt_value

DATA_DIR = Path.home() / ".slide-alchemy"
CONFIG_FILE = DATA_DIR / "config.enc"
PREFERENCES_FILE = DATA_DIR / "preferences.json"
PATTERNS_DB = DATA_DIR / "patterns.db"
PROJECTS_DIR = DATA_DIR / "projects"


def ensure_data_dir() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    PROJECTS_DIR.mkdir(parents=True, exist_ok=True)


def save_settings(settings: AppSettings) -> None:
    ensure_data_dir()
    data = settings.model_dump_json()
    encrypted = encrypt_value(data)
    CONFIG_FILE.write_text(encrypted)


def load_settings() -> AppSettings:
    ensure_data_dir()
    if not CONFIG_FILE.exists():
        return AppSettings()
    try:
        encrypted = CONFIG_FILE.read_text()
        decrypted = decrypt_value(encrypted)
        return AppSettings.model_validate_json(decrypted)
    except Exception as e:
        logger.warning(f"Failed to load settings, using defaults: {e}")
        return AppSettings()


def save_project_data(project_id: str, data: dict) -> None:
    ensure_data_dir()
    project_file = PROJECTS_DIR / f"{project_id}.json"
    project_file.write_text(json.dumps(data, indent=2, default=str))


def load_project_data(project_id: str) -> Optional[dict]:
    project_file = PROJECTS_DIR / f"{project_id}.json"
    if not project_file.exists():
        return None
    return json.loads(project_file.read_text())


def list_projects() -> list[dict]:
    ensure_data_dir()
    projects = []
    for f in PROJECTS_DIR.glob("*.json"):
        try:
            data = json.loads(f.read_text())
            projects.append(data)
        except Exception:
            continue
    return sorted(projects, key=lambda p: p.get("updated_at", ""), reverse=True)
