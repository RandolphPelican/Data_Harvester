"""Zenodo — Open research repository (free, no key required for search)."""
from harvester.clients.base import BaseClient


class ZenodoClient(BaseClient):
    SOURCE_NAME = "Zenodo"
    BASE_URL = "https://zenodo.org/api/records"

    def fetch(self, query: str, max_results: int = 25) -> list:
        params = {
            "q": query,
            "size": min(max_results, 100),
            "sort": "bestmatch",
        }

        resp = self._get(self.BASE_URL, params=params)
        hits = resp.json().get("hits", {}).get("hits", [])

        results = []
        for item in hits:
            meta = item.get("metadata", {})

            # Authors
            creators = meta.get("creators", [])
            authors = []
            for c in creators[:5]:
                name = c.get("name", "")
                if name:
                    authors.append(name)
            if len(creators) > 5:
                authors.append("et al.")

            # Year
            year = None
            pub_date = meta.get("publication_date", "")
            if pub_date and len(pub_date) >= 4:
                try:
                    year = int(pub_date[:4])
                except ValueError:
                    pass

            # DOI
            doi = item.get("doi", "") or meta.get("doi", "")

            # Link
            link = ""
            if doi:
                link = f"https://doi.org/{doi}"
            elif item.get("links", {}).get("html"):
                link = item["links"]["html"]

            # Abstract / description
            abstract = meta.get("description", "") or ""
            # Strip HTML tags from Zenodo descriptions
            import re
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
#..
