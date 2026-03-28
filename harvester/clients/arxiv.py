"""arXiv — Atom feed API (free, no key required)."""
import urllib.parse
import feedparser
from harvester.clients.base import BaseClient


class ArxivClient(BaseClient):
    SOURCE_NAME = "arXiv"
    BASE_URL = "http://export.arxiv.org/api/query"

    def fetch(self, query: str, max_results: int = 25) -> list:
        safe_q = urllib.parse.quote(query)
        url = f"{self.BASE_URL}?search_query=all:{safe_q}&start=0&max_results={max_results}"

        feed = feedparser.parse(url)

        results = []
        for entry in feed.entries:
            authors = ", ".join(a.name for a in entry.get("authors", [])[:5])
            if len(entry.get("authors", [])) > 5:
                authors += ", et al."

            year = None
            pub = entry.get("published", "")
            if pub and len(pub) >= 4:
                try:
                    year = int(pub[:4])
                except ValueError:
                    pass

            results.append(self._normalize(
                title=entry.get("title", "").replace("\n", " ").strip(),
                authors=authors,
                year=year,
                link=entry.get("link", ""),
                abstract=entry.get("summary", "").replace("\n", " ").strip(),
            ))

        return results
#..
