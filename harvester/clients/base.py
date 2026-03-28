"""
Base class for all harvester API clients.
"""
import time
import requests


class BaseClient:
    """All API clients inherit from this."""

    SOURCE_NAME = "unknown"
    REQUIRES_KEY = False
    TIMEOUT = 30
    MAX_RETRIES = 3

    def fetch(self, query: str, max_results: int = 25) -> list:
        """
        Fetch results for a query. Returns list of dicts with at minimum:
            { title, source, authors?, year?, doi?, link?, abstract? }
        """
        raise NotImplementedError

    def _get(self, url: str, params: dict = None, headers: dict = None) -> requests.Response:
        """GET with timeout, retry on 429/5xx, exponential backoff."""
        for attempt in range(self.MAX_RETRIES):
            resp = requests.get(url, params=params, headers=headers, timeout=self.TIMEOUT)
            if resp.status_code == 429 or resp.status_code >= 500:
                wait = (2 ** attempt) + 0.5
                time.sleep(wait)
                continue
            resp.raise_for_status()
            return resp
        # Final attempt — let it raise
        resp.raise_for_status()
        return resp

    def _normalize(self, title="", authors="", year=None, doi="", link="", abstract="", **extra) -> dict:
        """Produce a standardized result dict."""
        result = {
            "title": (title or "").strip(),
            "source": self.SOURCE_NAME,
            "authors": (authors or "").strip(),
            "year": year,
            "doi": (doi or "").strip(),
            "link": (link or "").strip(),
            "abstract": (abstract or "").strip(),
        }
        result.update(extra)
        return result
#..
