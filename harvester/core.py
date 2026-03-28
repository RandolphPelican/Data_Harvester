"""
Pelican Harvester — Core Engine
Orchestrates individual API clients and manages result storage.
"""
import os
import json
import csv
import time
from datetime import datetime, timezone

from harvester.config import Config
from harvester.clients.pubmed import PubMedClient
from harvester.clients.arxiv import ArxivClient
from harvester.clients.crossref import CrossrefClient
from harvester.clients.semantic_scholar import SemanticScholarClient
from harvester.clients.openalex import OpenAlexClient
from harvester.clients.europe_pmc import EuropePMCClient
from harvester.clients.doaj import DOAJClient
from harvester.clients.core_api import COREClient
from harvester.clients.unpaywall import UnpaywallClient
from harvester.clients.ieee import IEEEClient
from harvester.clients.springer import SpringerClient
from harvester.clients.scopus import ScopusClient
from harvester.clients.zenodo import ZenodoClient
from harvester.clients.osf import OSFClient


# Map source IDs to client classes
CLIENT_MAP = {
    "pubmed":     PubMedClient,
    "arxiv":      ArxivClient,
    "crossref":   CrossrefClient,
    "semantic":   SemanticScholarClient,
    "openalex":   OpenAlexClient,
    "europe_pmc": EuropePMCClient,
    "doaj":       DOAJClient,
    "core":       COREClient,
    "unpaywall":  UnpaywallClient,
    "ieee":       IEEEClient,
    "springer":   SpringerClient,
    "scopus":     ScopusClient,
    "zenodo":     ZenodoClient,
    "osf":        OSFClient,
}

# Politeness delay between API calls (seconds)
REQUEST_DELAY = 0.5


class HarvesterEngine:

    def __init__(self, config: Config):
        self.config = config
        self._clients = {}
        self._init_clients()

    def _init_clients(self):
        """Instantiate all clients with config-provided credentials."""
        cfg = self.config
        self._clients = {
            "pubmed":     PubMedClient(email=cfg.get("pubmed_email")),
            "arxiv":      ArxivClient(),
            "crossref":   CrossrefClient(),
            "semantic":   SemanticScholarClient(),
            "openalex":   OpenAlexClient(),
            "europe_pmc": EuropePMCClient(),
            "doaj":       DOAJClient(),
            "core":       COREClient(api_key=cfg.get("core_api_key")),
            "unpaywall":  UnpaywallClient(email=cfg.get("unpaywall_email")),
            "ieee":       IEEEClient(api_key=cfg.get("ieee_api_key")),
            "springer":   SpringerClient(api_key=cfg.get("springer_api_key")),
            "scopus":     ScopusClient(api_key=cfg.get("scopus_api_key")),
            "zenodo":     ZenodoClient(),
            "osf":        OSFClient(),
        }

    def harvest_single(self, source_id: str, query: str, max_results: int = 25) -> list:
        """Fetch results from a single source. Returns list of dicts."""
        client = self._clients.get(source_id)
        if not client:
            raise ValueError(f"Unknown source: {source_id}")

        results = client.fetch(query, max_results=max_results)
        time.sleep(REQUEST_DELAY)
        return results

    def save_to_vault(self, results: list, query: str, fmt: str = "json") -> str:
        """
        Save results to the vault directory.
        Returns the file path written.
        """
        vault = self.config.vault_dir
        os.makedirs(vault, exist_ok=True)

        ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        safe_query = "".join(c if c.isalnum() or c in " _-" else "" for c in query)[:40].strip().replace(" ", "_")

        if fmt == "csv":
            return self._save_csv(results, vault, safe_query, ts)
        elif fmt == "bibtex":
            return self._save_bibtex(results, vault, safe_query, ts)
        else:
            return self._save_json(results, vault, safe_query, ts, query)

    def _save_json(self, results, vault, safe_query, ts, raw_query):
        filename = f"harvest_{safe_query}_{ts}.json"
        path = os.path.join(vault, filename)

        payload = {
            "query": raw_query,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "total_results": len(results),
            "results": results,
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)

        self._write_provenance(raw_query, len(results), path)
        return path

    def _save_csv(self, results, vault, safe_query, ts):
        filename = f"harvest_{safe_query}_{ts}.csv"
        path = os.path.join(vault, filename)

        if not results:
            return path

        # Collect all unique keys across results
        all_keys = []
        for r in results:
            for k in r.keys():
                if k not in all_keys:
                    all_keys.append(k)

        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=all_keys, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(results)

        return path

    def _save_bibtex(self, results, vault, safe_query, ts):
        filename = f"harvest_{safe_query}_{ts}.bib"
        path = os.path.join(vault, filename)

        with open(path, "w", encoding="utf-8") as f:
            for i, r in enumerate(results):
                key = r.get("doi", "").replace("/", "_") or f"entry{i}"
                f.write(f"@article{{{key},\n")
                f.write(f"  title = {{{r.get('title', '')}}},\n")
                if r.get("authors"):
                    f.write(f"  author = {{{r['authors']}}},\n")
                if r.get("year"):
                    f.write(f"  year = {{{r['year']}}},\n")
                if r.get("doi"):
                    f.write(f"  doi = {{{r['doi']}}},\n")
                if r.get("source"):
                    f.write(f"  note = {{Source: {r['source']}}},\n")
                f.write("}\n\n")

        return path

    def _write_provenance(self, query, count, save_path):
        """Log harvest provenance."""
        logs_dir = self.config.logs_dir
        os.makedirs(logs_dir, exist_ok=True)
        ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        log_path = os.path.join(logs_dir, f"provenance_{ts}.json")

        entry = {
            "query": query,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "total_results": count,
            "saved_to": save_path,
        }
        with open(log_path, "w", encoding="utf-8") as f:
            json.dump(entry, f, indent=2)
#..
