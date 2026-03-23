class CrossrefClient:
    def __init__(self):
        pass

    def search(self, term, retmax=10):
        # Stub: return empty list for now
        return []

    def fetch_abstracts(self, id_list):
        # Stub: return empty list
        return []
# --- Test / Dry-run client ---
class TestCrossrefClient:
    def fetch(self, query):
        return [{"title": "Test Crossref Article", "doi": "10.1234/xyz"}]
