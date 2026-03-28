"""Scopus — Elsevier abstract and citation database (requires API key from dev.elsevier.com)."""
from harvester.clients.base import BaseClient


class ScopusClient(BaseClient):
    SOURCE_NAME = "Scopus"
    REQUIRES_KEY = True
    BASE_URL = "https://api.elsevier.com/content/search/scopus"

    def __init__(self, api_key: str = None):
        self.api_key = api_key or ""

    def fetch(self, query: str, max_results: int = 25) -> list:
        if not self.api_key:
            raise ValueError("Scopus requires an API key — register at dev.elsevier.com")

        headers = {
            "X-ELS-APIKey": self.api_key,
            "Accept": "application/json",
        }
        params = {
            "query": query,
            "count": min(max_results, 25),
        }

        resp = self._get(self.BASE_URL, params=params, headers=headers)
        entries = resp.json().get("search-results", {}).get("entry", [])

        results = []
        for item in entries:
            title = item.get("dc:title", "")
            authors = item.get("dc:creator", "")

            year = None
            cover_date = item.get("prism:coverDate", "")
            if cover_date and len(cover_date) >= 4:
                try:
                    year = int(cover_date[:4])
                except ValueError:
                    pass

            doi = item.get("prism:doi", "")

            # Find the Scopus link
            link = ""
            for lnk in item.get("link", []):
                if lnk.get("@ref") == "scopus":
                    link = lnk.get("@href", "")
                    break

            results.append(self._normalize(
                title=title,
                authors=authors,
                year=year,
                doi=doi,
                link=link,
                abstract=item.get("dc:description", ""),
            ))

        return results
#..
