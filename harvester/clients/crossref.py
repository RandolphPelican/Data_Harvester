"""Crossref — REST API (free, no key required)."""
from harvester.clients.base import BaseClient


class CrossrefClient(BaseClient):
    SOURCE_NAME = "Crossref"
    BASE_URL = "https://api.crossref.org/works"

    def fetch(self, query: str, max_results: int = 25) -> list:
        params = {
            "query": query,
            "rows": max_results,
            "select": "DOI,title,author,published-print,published-online,abstract,URL",
        }
        headers = {
            "User-Agent": "PelicanHarvester/1.0 (mailto:pelicanharvester@example.com)",
        }

        resp = self._get(self.BASE_URL, params=params, headers=headers)
        items = resp.json().get("message", {}).get("items", [])

        results = []
        for item in items:
            title = ""
            title_list = item.get("title", [])
            if title_list:
                title = title_list[0]

            authors = []
            for a in item.get("author", [])[:5]:
                name = f"{a.get('family', '')} {a.get('given', '')}".strip()
                if name:
                    authors.append(name)
            if len(item.get("author", [])) > 5:
                authors.append("et al.")

            year = None
            for date_key in ("published-print", "published-online"):
                dp = item.get(date_key, {}).get("date-parts", [[]])
                if dp and dp[0] and dp[0][0]:
                    year = dp[0][0]
                    break

            doi = item.get("DOI", "")
            abstract = item.get("abstract", "")
            # Crossref abstracts sometimes have JATS XML tags
            if abstract:
                import re
                abstract = re.sub(r"<[^>]+>", "", abstract).strip()

            results.append(self._normalize(
                title=title,
                authors=", ".join(authors),
                year=year,
                doi=doi,
                link=item.get("URL", ""),
                abstract=abstract,
            ))

        return results
#..
