"""IEEE Xplore — Engineering and CS research (requires API key from developer.ieee.org)."""
from harvester.clients.base import BaseClient


class IEEEClient(BaseClient):
    SOURCE_NAME = "IEEE Xplore"
    REQUIRES_KEY = True
    BASE_URL = "https://ieeexploreapi.ieee.org/api/v1/search/articles"

    def __init__(self, api_key: str = None):
        self.api_key = api_key or ""

    def fetch(self, query: str, max_results: int = 25) -> list:
        if not self.api_key:
            raise ValueError("IEEE Xplore requires an API key — register at developer.ieee.org")

        params = {
            "querytext": query,
            "max_records": min(max_results, 200),
            "apikey": self.api_key,
        }

        resp = self._get(self.BASE_URL, params=params)
        items = resp.json().get("articles", [])

        results = []
        for item in items:
            authors_raw = item.get("authors", {}).get("authors", [])
            authors = ", ".join(
                a.get("full_name", "") for a in authors_raw[:5]
            )
            if len(authors_raw) > 5:
                authors += ", et al."

            year = item.get("publication_year")
            if year and str(year).isdigit():
                year = int(year)

            results.append(self._normalize(
                title=item.get("title", ""),
                authors=authors,
                year=year,
                doi=item.get("doi", ""),
                link=item.get("html_url", ""),
                abstract=item.get("abstract", ""),
            ))

        return results
#..
