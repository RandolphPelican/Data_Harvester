# Production client placeholder
class SemanticScholarClient:
    def fetch(self, query):
        # Real API logic will go here later
        raise NotImplementedError("Live Semantic Scholar client not implemented yet")


# --- Test / Dry-run client ---
class TestSemanticScholarClient:
    def fetch(self, query):
        return [
            {
                "title": "Test Semantic Scholar Paper",
                "id": "SS-001",
                "query": query
            }
        ]
