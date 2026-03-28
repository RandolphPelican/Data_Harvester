"""CORE — Open access research aggregator (free key available at core.ac.uk)."""
from harvester.clients.base import BaseClient


class COREClient(BaseClient):
    SOURCE_NAME = "CORE"
    REQUIRES_KEY = True
    BASE_URL = "https://api.core.ac.uk/v3/search/works"

    def __init__(self, api_key: str = None):
        self.api_key = api_key or ""

    def fetch(self, query: str, max_results: int = 25) -> list:
        if not self.api_key:
            raise ValueError("CORE requires an API key — get one free at core.ac.uk/services/api")

        headers = {"Authorization": f"Bearer {self.api_key}"}
        params = {"q": query, "limit": min(max_results, 100)}

        resp = self._get(self.BASE_URL, params=params, headers=headers)
        items = resp.json().get("results", [])

        results = []
        for item in items:
            authors = []
            for a in (item.get("authors") or [])[:5]:
                name = a.get("name", "") if isinstance(a, dict) else str(a)
                if name:
                    authors.append(name)

            year = item.get("yearPublished")
            doi = ""
            for ident in (item.get("identifiers") or []):
                if isinstance(ident, str) and ident.startswith("10."):
                    doi = ident
                    break

            results.append(self._normalize(
                title=item.get("title", ""),
                authors=", ".join(authors),
                year=year,
                doi=doi,
                link=item.get("downloadUrl", "") or item.get("sourceFulltextUrls", [""])[0] if item.get("sourceFulltextUrls") else "",
                abstract=item.get("abstract", "") or "",
            ))

        return results
#..
