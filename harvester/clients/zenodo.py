"""Zenodo — Open research repository (free, no key required).
Searches general terms AND creator names to maximize results.
Supports ORCID, DOI, and record ID patterns.
"""
import re
from harvester.clients.base import BaseClient


class ZenodoClient(BaseClient):
    SOURCE_NAME = "Zenodo"
    BASE_URL = "https://zenodo.org/api/records"

    def fetch(self, query: str, max_results: int = 25) -> list:
        q = query.strip()

        # Special patterns: ORCID, DOI, record ID
        if re.match(r"^\d{4}-\d{4}-\d{4}-\d{3}[\dX]$", q):
            return self._search(f"creators.orcid:{q}", max_results)
        if q.startswith("10.") or q.startswith("doi:"):
            return self._search(f"doi:{q.replace('doi:','').strip()}", max_results)
        if re.match(r"^\d{5,}$", q):
            return self._search(f"recid:{q}", max_results)

        # General search: run BOTH general and creator name queries
        half = max(max_results // 2, 5)
        general = self._search(q, half)
        creator = self._search(f'creators.name:"{q}"', half)

        # Also try with words reversed (John Stabler -> Stabler, John)
        words = q.split()
        if len(words) == 2:
            reversed_name = f"{words[1]}, {words[0]}"
            creator += self._search(f'creators.name:"{reversed_name}"', half)

        # Deduplicate by DOI or title
        seen = set()
        merged = []
        for r in creator + general:
            key = r.get("doi") or r.get("title", "")
            if key and key not in seen:
                seen.add(key)
                merged.append(r)

        return merged[:max_results]

    def _search(self, zen_query: str, size: int) -> list:
        params = {"q": zen_query, "size": min(size, 100), "sort": "bestmatch"}
        try:
            resp = self._get(self.BASE_URL, params=params)
            hits = resp.json().get("hits", {}).get("hits", [])
        except Exception:
            return []

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
            link = f"https://doi.org/{doi}" if doi else item.get("links", {}).get("html", "")
            abstract = meta.get("description", "") or ""
            abstract = re.sub(r"<[^>]+>", "", abstract).strip()

            results.append(self._normalize(
                title=meta.get("title", ""),
                authors=", ".join(authors),
                year=year,
                doi=doi,
                link=link,
                abstract=abstract,
            ))
        return results
#..
