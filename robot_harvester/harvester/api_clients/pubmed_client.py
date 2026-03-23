class PubMedClient:
    def __init__(self, email):
        self.email = email

    def fetch(self, query):
        # placeholder: return dummy data for testing
        return [{"title": "Test PubMed Article", "id": "123456"}]
 # --- Test / Dry-run client ---
class TestPubMedClient:
    def fetch(self, query):
        return [{"title": "Test PubMed Article", "pmid": "123456"}]
