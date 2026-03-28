"""
Pelican Harvester — Configuration
System-agnostic paths and persistent settings.
"""
import os
import json
from pathlib import Path


def _default_base_dir() -> str:
    """Cross-platform default: ~/Documents/PelicanHarvester"""
    return str(Path.home() / "Documents" / "PelicanHarvester")


class Config:
    SETTINGS_FILE = "settings.json"

    DEFAULTS = {
        "base_dir": _default_base_dir(),
        "pubmed_email": "",
        "openalex_email": "",
        "core_api_key": "",
        "unpaywall_email": "",
        "semantic_api_key": "",
        "ieee_api_key": "",
        "springer_api_key": "",
        "scopus_api_key": "",
    }

    def __init__(self):
        self._data = dict(self.DEFAULTS)
        self._ensure_dirs()
        self._load()

    # ── Paths ──
    @property
    def base_dir(self) -> str:
        return self._data.get("base_dir", _default_base_dir())

    @property
    def vault_dir(self) -> str:
        d = self._data.get("vault_dir", "")
        return d if d else os.path.join(self.base_dir, "vault")

    @property
    def logs_dir(self) -> str:
        return os.path.join(self.base_dir, "logs")

    @property
    def settings_path(self) -> str:
        return os.path.join(self.base_dir, self.SETTINGS_FILE)

    # ── Getters ──
    def get(self, key: str, default=None):
        return self._data.get(key, default)

    def to_dict(self) -> dict:
        d = dict(self._data)
        d["vault_dir"] = self.vault_dir
        d["logs_dir"] = self.logs_dir
        return d

    # ── Update and persist ──
    def update(self, data: dict):
        for k, v in data.items():
            if k in self.DEFAULTS or k == "vault_dir":
                self._data[k] = v

    def save(self):
        self._ensure_dirs()
        with open(self.settings_path, "w", encoding="utf-8") as f:
            json.dump(self._data, f, indent=2)

    # ── Internal ──
    def _ensure_dirs(self):
        os.makedirs(self.base_dir, exist_ok=True)
        os.makedirs(self.vault_dir, exist_ok=True)
        os.makedirs(self.logs_dir, exist_ok=True)

    def _load(self):
        if os.path.exists(self.settings_path):
            try:
                with open(self.settings_path, "r", encoding="utf-8") as f:
                    saved = json.load(f)
                self._data.update(saved)
            except (json.JSONDecodeError, IOError):
                pass
        else:
            self.save()
#..
