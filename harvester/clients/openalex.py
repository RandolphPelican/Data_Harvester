"""OpenAlex — Open catalog of scholarly works (free, no key required)."""
from harvester.clients.base import BaseClient


class OpenAlexClient(BaseClient):
    SOURCE_NAME = "OpenAlex"
    BASE_URL = "https://api.openalex.org/works"

    def fetch(self, query: str, max_results: int = 25) -> list:
        params = {
            "search": query,
            "per_page": min(max_results, 200),
            "select": "id,doi,title,authorships,publication_year,primary_location,abstract_inverted_index",
        }
        headers = {
            "User-Agent": "PelicanHarvester/1.0",
        }

        resp = self._get(self.BASE_URL, params=params, headers=headers)
        items = resp.json().get("results", [])

        results = []
        for item in items:
            # Authors
            authors = []
            for a in (item.get("authorships") or [])[:5]:
                name = a.get("author", {}).get("display_name", "")
                if name:
                    authors.append(name)
            if len(item.get("authorships") or []) > 5:
                authors.append("et al.")

            # DOI — strip the https://doi.org/ prefix
            doi_raw = item.get("doi", "") or ""
            doi = doi_raw.replace("https://doi.org/", "")

            # Abstract from inverted index
            abstract = self._reconstruct_abstract(item.get("abstract_inverted_index"))

            # Link
            link = ""
            loc = item.get("primary_location") or {}
            landing = loc.get("landing_page_url", "")
            if landing:
                link = landing

            results.append(self._normalize(
                title=item.get("title", "") or "",
                authors=", ".join(authors),
                year=item.get("publication_year"),
                doi=doi,
                link=link,
                abstract=abstract,
            ))

        return results

    @staticmethod
    def _reconstruct_abstract(inverted_index: dict) -> str:
        """OpenAlex stores abstracts as inverted index: {word: [positions]}."""
        if not inverted_index:
            return ""
        try:
            words = {}
            for word, positions in inverted_index.items():
                for pos in positions:
                    words[pos] = word
            return " ".join(words[k] for k in sorted(words.keys()))
        except Exception:
            return ""
#..
