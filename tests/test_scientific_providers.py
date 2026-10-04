import unittest

from engines.scientific_research.provider import ScientificProvider
from engines.scientific_research.crossref_client import CrossrefClient
from engines.scientific_research.pubmed_client import PubMedClient
from engines.scientific_research.scopus_client import ScopusClient
from engines.scientific_research.semantic_scholar_client import SemanticScholarClient
from engines.scientific_research.parser import normalize_result


class ProviderContractTests(unittest.TestCase):
    def test_provider_is_callable(self):
        class MockProvider(ScientificProvider):
            def search(self, query):
                return [{"title": query}]

        self.assertEqual(MockProvider()("test")[0]["title"], "test")

    def test_adapters_delegate_without_http_dependency(self):
        clients = [
            CrossrefClient(lambda q: [{"title": q}]),
            PubMedClient(lambda q: [{"title": q}]),
            ScopusClient(lambda q: [{"title": q}]),
            SemanticScholarClient(lambda q: [{"title": q}]),
        ]
        for client in clients:
            self.assertEqual(client.search("query")[0]["title"], "query")

    def test_unconfigured_adapter_fails_explicitly(self):
        with self.assertRaises(RuntimeError):
            CrossrefClient().search("query")

    def test_normalizer_preserves_data_and_adds_context(self):
        result = normalize_result(
            {"title": "Study", "doi": "10.1000/test"},
            provider="crossref",
            query="skin",
        )
        self.assertEqual(result["title"], "Study")
        self.assertEqual(result["provider"], "crossref")
        self.assertEqual(result["query"], "skin")


if __name__ == "__main__":
    unittest.main()
