"""PubMed — NCBI E-utilities (free, no key required)."""
import xml.etree.ElementTree as ET
from harvester.clients.base import BaseClient


class PubMedClient(BaseClient):
    SOURCE_NAME = "PubMed"
    SEARCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    FETCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"

    def __init__(self, email: str = None):
        self.email = email or ""

    def fetch(self, query: str, max_results: int = 25) -> list:
        # Step 1: Search for IDs
        params = {
            "db": "pubmed",
            "term": query,
            "retmax": max_results,
            "retmode": "json",
        }
        if self.email:
            params["email"] = self.email

        resp = self._get(self.SEARCH_URL, params=params)
        id_list = resp.json().get("esearchresult", {}).get("idlist", [])
        if not id_list:
            return []

        # Step 2: Fetch article details
        params = {
            "db": "pubmed",
            "id": ",".join(id_list),
            "retmode": "xml",
        }
        if self.email:
            params["email"] = self.email

        resp = self._get(self.FETCH_URL, params=params)
        root = ET.fromstring(resp.text)

        results = []
        for article in root.findall(".//PubmedArticle"):
            title_el = article.find(".//ArticleTitle")
            title = title_el.text if title_el is not None else "Untitled"

            pmid_el = article.find(".//PMID")
            pmid = pmid_el.text if pmid_el is not None else ""

            abstract_el = article.find(".//Abstract/AbstractText")
            abstract = abstract_el.text if abstract_el is not None else ""

            # Authors
            author_els = article.findall(".//Author")
            authors = []
            for a in author_els[:5]:
                last = a.findtext("LastName", "")
                init = a.findtext("Initials", "")
                if last:
                    authors.append(f"{last} {init}".strip())
            if len(author_els) > 5:
                authors.append("et al.")

            # Year
            year_el = article.find(".//PubDate/Year")
            year = int(year_el.text) if year_el is not None and year_el.text.isdigit() else None

            # DOI
            doi = ""
            for aid in article.findall(".//ArticleId"):
                if aid.get("IdType") == "doi":
                    doi = aid.text or ""
                    break

            results.append(self._normalize(
                title=title,
                authors=", ".join(authors),
                year=year,
                doi=doi,
                link=f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/" if pmid else "",
                abstract=abstract,
                pmid=pmid,
            ))

        return results
#..
