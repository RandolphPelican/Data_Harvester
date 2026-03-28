"""Unpaywall — Find open access versions of papers (free, requires email)."""
from harvester.clients.base import BaseClient


class UnpaywallClient(BaseClient):
    SOURCE_NAME = "Unpaywall"
    BASE_URL = "https://api.unpaywall.org/v2/search"

    def __init__(self, email: str = None):
        self.email = email or ""

    def fetch(self, query: str, max_results: int = 25) -> list:
        if not self.email:
            raise ValueError("Unpaywall requires an email address in Settings")

        params = {
            "query": query,
            "email": self.email,
        }

        resp = self._get(self.BASE_URL, params=params)
        items = resp.json().get("results", [])[:max_results]

        results = []
        for item in items:
            r = item.get("response", {})
            title = r.get("title", "")
            doi = r.get("doi", "")
            year = r.get("year")

            # Get OA link
            link = ""
            best_oa = r.get("best_oa_location") or {}
            link = best_oa.get("url_for_landing_page", "") or best_oa.get("url", "")
            if not link and doi:
                link = f"https://doi.org/{doi}"

            z_authors = r.get("z_authors") or []
            authors = []
            for a in z_authors[:5]:
                name = f"{a.get('family', '')} {a.get('given', '')}".strip()
                if name:
                    authors.append(name)
            if len(z_authors) > 5:
                authors.append("et al.")

            results.append(self._normalize(
                title=title,
                authors=", ".join(authors),
                year=year,
                doi=doi,
                link=link,
                is_oa=r.get("is_oa", False),
            ))

        return results
#..
