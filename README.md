# Pelican Harvester

**Desktop research data aggregator.** Search 12 academic databases from a single interface, save results to your local vault in JSON, CSV, or BibTeX.

## Quick Start

### Windows
1. Install [Python 3.10+](https://www.python.org/downloads/) (check "Add to PATH")
2. Double-click `PelicanHarvester.bat`
3. First launch auto-installs dependencies

### macOS / Linux
```bash
chmod +x pelican_harvester.sh
./pelican_harvester.sh
```

### Manual Install
```bash
pip install -r requirements.txt
python main.py
```

## Databases

| Database | Key Required | Domain |
|----------|:---:|--------|
| PubMed | No | Biomedical |
| arXiv | No | Preprints |
| Crossref | No | DOI Metadata |
| Semantic Scholar | No | AI-Powered |
| OpenAlex | No | Open Catalog |
| Europe PMC | No | EU Biomedical |
| DOAJ | No | Open Access Journals |
| CORE | Free key | OA Research |
| Unpaywall | Email | OA Finder |
| IEEE Xplore | Yes | Engineering |
| Springer Nature | Yes | Multidisciplinary |
| Scopus | Yes | Elsevier |

## Output Formats

- **JSON** — Full structured data with metadata
- **CSV** — Spreadsheet-compatible flat format  
- **BibTeX** — Ready for LaTeX / reference managers

## Project Structure

```
pelican_harvester/
├── main.py                  # Entry point (PyWebView launcher)
├── PelicanHarvester.bat     # Windows double-click launcher
├── pelican_harvester.sh     # macOS/Linux launcher
├── requirements.txt
├── harvester/
│   ├── config.py            # Settings and path management
│   ├── core.py              # Harvest engine and save logic
│   └── clients/
│       ├── base.py          # Base client class
│       ├── pubmed.py        # PubMed (NCBI E-utilities)
│       ├── arxiv.py         # arXiv (Atom API)
│       ├── crossref.py      # Crossref (REST API)
│       ├── semantic_scholar.py
│       ├── openalex.py      # OpenAlex
│       ├── europe_pmc.py    # Europe PMC
│       ├── doaj.py          # DOAJ
│       ├── core_api.py      # CORE
│       ├── unpaywall.py     # Unpaywall
│       ├── ieee.py          # IEEE Xplore
│       ├── springer.py      # Springer Nature
│       └── scopus.py        # Scopus / Elsevier
└── ui/
    └── index.html           # Frontend (HTML/CSS/JS)
```

## Data Storage

All results save to `~/Documents/PelicanHarvester/vault/` by default.  
Configurable in Settings (⚙).

## License

MIT

---

*Built by Randolph Pelican III / StableTech Enterprises LLC*
