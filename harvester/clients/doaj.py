"""DOAJ — Directory of Open Access Journals (free, no key required)."""
from harvester.clients.base import BaseClient


class DOAJClient(BaseClient):
    SOURCE_NAME = "DOAJ"
    BASE_URL = "https://doaj.org/api/search/articles"

    def fetch(self, query: str, max_results: int = 25) -> list:
        url = f"{self.BASE_URL}/{query}"
        params = {
            "pageSize": min(max_results, 100),
            "page": 1,
        }

        resp = self._get(url, params=params)
        items = resp.json().get("results", [])

        results = []
        for item in items:
            bib = item.get("bibjson", {})
            title = bib.get("title", "")

            authors = []
            for a in bib.get("author", [])[:5]:
                name = a.get("name", "")
                if name:
                    authors.append(name)
            if len(bib.get("author", [])) > 5:
                authors.append("et al.")

            year = bib.get("year")
            if year and str(year).isdigit():
                year = int(year)
            else:
                year = None

            doi = ""
            link = ""
            for ident in bib.get("identifier", []):
                if ident.get("type") == "doi":
                    doi = ident.get("id", "")
                    link = f"https://doi.org/{doi}"

            if not link:
                for lnk in bib.get("link", []):
                    if lnk.get("url"):
                        link = lnk["url"]
                        break

            abstract_text = bib.get("abstract", "") or ""

            results.append(self._normalize(
                title=title,
                authors=", ".join(authors),
                year=year,
                doi=doi,
                link=link,
                abstract=abstract_text,
            ))

        return results
#..
