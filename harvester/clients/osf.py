"""OSF — Open Science Framework (free, no key required for search)."""
from harvester.clients.base import BaseClient


class OSFClient(BaseClient):
    SOURCE_NAME = "OSF"
    BASE_URL = "https://api.osf.io/v2/search/"

    def fetch(self, query: str, max_results: int = 25) -> list:
        params = {
            "q": query,
            "page[size]": min(max_results, 100),
        }

        resp = self._get(self.BASE_URL, params=params)
        items = resp.json().get("data", [])

        results = []
        for item in items:
            item_type = item.get("type", "")
            attrs = item.get("attributes", {})

            # Only process nodes (projects), registrations, preprints
            if item_type not in ("nodes", "registrations", "preprints"):
                continue

            title = attrs.get("title", "")
            if not title:
                continue

            description = attrs.get("description", "") or ""

            # Get links
            link = ""
            links = item.get("links", {})
            if links.get("html"):
                link = links["html"]

            # Get DOI if available
            doi = ""
            article_doi = attrs.get("doi", "")
            if article_doi:
                doi = article_doi
            elif attrs.get("preprint_doi_created"):
                doi = attrs.get("preprint_doi_created", "")

            # Year from date_created or date_published
            year = None
            for date_key in ("date_published", "date_created"):
                date_str = attrs.get(date_key, "")
                if date_str and len(date_str) >= 4:
                    try:
                        year = int(date_str[:4])
                        break
                    except ValueError:
                        pass

            results.append(self._normalize(
                title=title,
                year=year,
                doi=doi,
                link=link,
                abstract=description[:500] if description else "",
                resource_type=item_type,
            ))

        return results
#..
