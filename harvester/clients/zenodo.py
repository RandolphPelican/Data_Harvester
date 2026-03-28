"""Zenodo — Open research repository (free, no key required).
Supports smart search: ORCID, DOI, author names, and general queries.
"""
import re
from harvester.clients.base import BaseClient


class ZenodoClient(BaseClient):
    SOURCE_NAME = "Zenodo"
    BASE_URL = "https://zenodo.org/api/records"

    def fetch(self, query: str, max_results: int = 25) -> list:
        q = query.strip()
        zen_query = self._build_query(q)

        params = {
            "q": zen_query,
            "size": min(max_results, 100),
            "sort": "bestmatch",
        }

        resp = self._get(self.BASE_URL, params=params)
        hits = resp.json().get("hits", {}).get("hits", [])

        # If general search returned nothing, try as creator name
        if not hits and not self._is_special_query(q):
            params["q"] = f'creators.name:"{q}"'
            resp = self._get(self.BASE_URL, params=params)
            hits = resp.json().get("hits", {}).get("hits", [])

        results = []
        for item in hits:
            meta = item.get("metadata", {})

            creators = meta.get("creators", [])
            authors = []
            for c in creators[:5]:
                name = c.get("name", "")
                if name:
                    authors.append(name)
            if len(creators) > 5:
                authors.append("et al.")

            year = None
            pub_date = meta.get("publication_date", "")
            if pub_date and len(pub_date) >= 4:
                try:
                    year = int(pub_date[:4])
                except ValueError:
                    pass

            doi = item.get("doi", "") or meta.get("doi", "")

            link = ""
            if doi:
                link = f"https://doi.org/{doi}"
            elif item.get("links", {}).get("html"):
                link = item["links"]["html"]

            abstract = meta.get("description", "") or ""
            abstract = re.sub(r"<[^>]+>", "", abstract).strip()

            results.append(self._normalize(
                title=meta.get("title", ""),
                authors=", ".join(authors),
                year=year,
                doi=doi,
                link=link,
                abstract=abstract,
                resource_type=meta.get("resource_type", {}).get("title", ""),
            ))

        return results

    def _build_query(self, q: str) -> str:
        """Detect ORCID, DOI, or record ID patterns and build proper Zenodo query."""
        # ORCID pattern: 0000-0000-0000-0000
        if re.match(r"^\d{4}-\d{4}-\d{4}-\d{3}[\dX]$", q):
            return f"creators.orcid:{q}"

        # DOI pattern
        if q.startswith("10.") or q.startswith("doi:"):
            doi = q.replace("doi:", "").strip()
            return f"doi:{doi}"

        # Zenodo record ID (just a number)
        if re.match(r"^\d{5,}$", q):
            return f"recid:{q}"

        # General search — pass through
        return q

    def _is_special_query(self, q: str) -> bool:
        """Check if query was already a special pattern."""
        return bool(
            re.match(r"^\d{4}-\d{4}-\d{4}-\d{3}[\dX]$", q) or
            q.startswith("10.") or
            q.startswith("doi:") or
            re.match(r"^\d{5,}$", q)
        )
#..
