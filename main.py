#!/usr/bin/env python3
"""
Pelican Harvester — Desktop Research Data Aggregator
Double-click to launch. Cross-platform via PyWebView.
"""
import sys
import os
import json
import subprocess
import platform
import threading
import webview

# Ensure project root is importable
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)

from harvester.core import HarvesterEngine
from harvester.config import Config


class PelicanAPI:
    """
    Python API exposed to the JavaScript frontend via PyWebView bridge.
    Every public method here is callable from JS as:
        window.pywebview.api.method_name(args)
    """

    def __init__(self):
        self.config = Config()
        self.engine = HarvesterEngine(self.config)

    # ── Harvest a single source ──
    def harvest_source(self, source_id: str, query: str, max_results: int = 25) -> str:
        """Fetch results from one database. Returns JSON string."""
        try:
            results = self.engine.harvest_single(source_id, query, max_results)
            return json.dumps(results, ensure_ascii=False)
        except Exception as e:
            return json.dumps({"error": str(e)})

    # ── Save results to vault ──
    def save_results(self, results_json: str, query: str, fmt: str = "json") -> str:
        """Save harvested results to the vault directory."""
        results = json.loads(results_json)
        path = self.engine.save_to_vault(results, query, fmt)
        return path

    # ── Settings ──
    def get_settings(self) -> str:
        return json.dumps(self.config.to_dict())

    def save_settings(self, settings_json: str) -> str:
        data = json.loads(settings_json)
        self.config.update(data)
        self.config.save()
        # Rebuild engine with new config
        self.engine = HarvesterEngine(self.config)
        return "ok"

    # ── Vault ──
    def get_vault_path(self) -> str:
        return self.config.vault_dir

    def open_vault(self) -> str:
        """Open the vault directory in the system file manager."""
        vault = self.config.vault_dir
        os.makedirs(vault, exist_ok=True)
        system = platform.system()
        try:
            if system == "Windows":
                os.startfile(vault)
            elif system == "Darwin":
                subprocess.Popen(["open", vault])
            else:
                subprocess.Popen(["xdg-open", vault])
        except Exception as e:
            return str(e)
        return "ok"


def main():
    api = PelicanAPI()
    ui_path = os.path.join(PROJECT_ROOT, "ui", "index.html")

    window = webview.create_window(
        title="Pelican Harvester",
        url=ui_path,
        js_api=api,
        width=1100,
        height=750,
        min_size=(900, 600),
        background_color="#060b18",
        text_select=False,
    )

    # Start the webview event loop
    webview.start(debug=("--debug" in sys.argv))


if __name__ == "__main__":
    main()
#..
