import json
import os
from datetime import datetime

from robot_harvester.harvester.api_clients.pubmed_client import TestPubMedClient
from robot_harvester.harvester.api_clients.crossref_client import TestCrossrefClient
from robot_harvester.harvester.api_clients.semantic_scholar_client import TestSemanticScholarClient


class Harvester:
    def __init__(self, query="robot anxiety"):
        self.query = query

        # Test / dry-run clients
        self.pubmed = TestPubMedClient()
        self.crossref = TestCrossrefClient()
        self.semantic = TestSemanticScholarClient()

        # Output paths
        self.base_dir = os.path.dirname(os.path.dirname(__file__))
        self.vault_dir = os.path.join(self.base_dir, "vault")
        self.logs_dir = os.path.join(self.base_dir, "logs")

        os.makedirs(self.vault_dir, exist_ok=True)
        os.makedirs(self.logs_dir, exist_ok=True)

    def run(self):
        timestamp = datetime.utcnow().isoformat()
        provenance = {
            "query": self.query,
            "timestamp": timestamp,
            "sources": {}
        }

        # Fetch from each source
        pubmed_data = self.pubmed.fetch(self.query)
        crossref_data = self.crossref.fetch(self.query)
        semantic_data = self.semantic.fetch(self.query)

        # Save results
        self._save_data("pubmed", pubmed_data)
        self._save_data("crossref", crossref_data)
        self._save_data("semantic_scholar", semantic_data)

        provenance["sources"]["pubmed"] = len(pubmed_data)
        provenance["sources"]["crossref"] = len(crossref_data)
        provenance["sources"]["semantic_scholar"] = len(semantic_data)

        self._save_provenance(provenance)

    def _save_data(self, source, data):
        filename = f"{source}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        path = os.path.join(self.vault_dir, filename)

        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def _save_provenance(self, provenance):
        filename = f"provenance_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        path = os.path.join(self.logs_dir, filename)

        with open(path, "w", encoding="utf-8") as f:
            json.dump(provenance, f, indent=2)
