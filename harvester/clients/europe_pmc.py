"""Europe PMC — European biomedical literature (free, no key required)."""
from harvester.clients.base import BaseClient


class EuropePMCClient(BaseClient):
    SOURCE_NAME = "Europe PMC"
    BASE_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"

    def fetch(self, query: str, max_results: int = 25) -> list:
        params = {
            "query": query,
            "format": "json",
            "pageSize": min(max_results, 100),
            "resultType": "core",
        }

        resp = self._get(self.BASE_URL, params=params)
        items = resp.json().get("resultList", {}).get("result", [])

        results = []
        for item in items:
            authors = item.get("authorString", "")
            year = None
            pub_year = item.get("pubYear")
            if pub_year and str(pub_year).isdigit():
                year = int(pub_year)

            doi = item.get("doi", "")
            pmid = item.get("pmid", "")
            link = ""
            if doi:
                link = f"https://doi.org/{doi}"
            elif pmid:
                link = f"https://europepmc.org/article/med/{pmid}"

            results.append(self._normalize(
                title=item.get("title", ""),
                authors=authors,
                year=year,
                doi=doi,
                link=link,
                abstract=item.get("abstractText", "") or "",
                pmid=pmid,
            ))

        return results
#..
