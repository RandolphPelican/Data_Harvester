"""Semantic Scholar — Academic Graph API (free, no key required)."""
from harvester.clients.base import BaseClient


class SemanticScholarClient(BaseClient):
    SOURCE_NAME = "Semantic Scholar"
    BASE_URL = "https://api.semanticscholar.org/graph/v1/paper/search"

    def fetch(self, query: str, max_results: int = 25) -> list:
        params = {
            "query": query,
            "limit": min(max_results, 100),
            "fields": "title,authors,year,abstract,externalIds,url",
        }

        resp = self._get(self.BASE_URL, params=params)
        data = resp.json().get("data", [])

        results = []
        for item in data:
            authors = []
            for a in (item.get("authors") or [])[:5]:
                name = a.get("name", "")
                if name:
                    authors.append(name)
            if len(item.get("authors") or []) > 5:
                authors.append("et al.")

            ext_ids = item.get("externalIds") or {}
            doi = ext_ids.get("DOI", "")

            results.append(self._normalize(
                title=item.get("title", ""),
                authors=", ".join(authors),
                year=item.get("year"),
                doi=doi,
                link=item.get("url", ""),
                abstract=item.get("abstract", "") or "",
            ))

        return results
#..
