"""Springer Nature — Multidisciplinary (requires API key from dev.springernature.com)."""
from harvester.clients.base import BaseClient


class SpringerClient(BaseClient):
    SOURCE_NAME = "Springer Nature"
    REQUIRES_KEY = True
    BASE_URL = "https://api.springernature.com/metadata/json"

    def __init__(self, api_key: str = None):
        self.api_key = api_key or ""

    def fetch(self, query: str, max_results: int = 25) -> list:
        if not self.api_key:
            raise ValueError("Springer Nature requires an API key — register at dev.springernature.com")

        params = {
            "q": query,
            "p": min(max_results, 50),
            "api_key": self.api_key,
        }

        resp = self._get(self.BASE_URL, params=params)
        items = resp.json().get("records", [])

        results = []
        for item in items:
            creators = item.get("creators", [])
            authors = ", ".join(c.get("creator", "") for c in creators[:5])
            if len(creators) > 5:
                authors += ", et al."

            year = None
            pub_date = item.get("publicationDate", "")
            if pub_date and len(pub_date) >= 4:
                try:
                    year = int(pub_date[:4])
                except ValueError:
                    pass

            doi = item.get("doi", "")

            results.append(self._normalize(
                title=item.get("title", ""),
                authors=authors,
                year=year,
                doi=doi,
                link=f"https://doi.org/{doi}" if doi else "",
                abstract=item.get("abstract", ""),
            ))

        return results
#..
