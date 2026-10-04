import unittest

from engines.scientific_research.provider import ScientificProvider
from engines.scientific_research.search_pipeline import ScientificSearchPipeline


class FakeProvider(ScientificProvider):
    def __init__(self, name, results):
        self.name = name
        self.results = results
        self.queries = []

    def search(self, query):
        self.queries.append(query)
        return self.results


class SearchPipelineTests(unittest.TestCase):
    def test_searches_selected_providers_and_normalizes_context(self):
        crossref = FakeProvider("crossref", [{"title": "Paper A", "doi": "10.1/a"}])
        pubmed = FakeProvider("pubmed", [{"title": "Paper B", "pmid": "2"}])
        pipeline = ScientificSearchPipeline([crossref, pubmed])

        results = pipeline.search("skin regeneration", providers=["crossref", "pubmed"])

        self.assertEqual(["skin regeneration"], crossref.queries)
        self.assertEqual(["skin regeneration"], pubmed.queries)
        self.assertEqual(2, len(results))
        self.assertEqual("crossref", results[0]["provider"])
        self.assertEqual("pubmed", results[1]["provider"])
        self.assertEqual("skin regeneration", results[0]["query"])

    def test_execute_returns_stable_envelope(self):
        provider = FakeProvider("crossref", [{"title": "Paper A"}])
        pipeline = ScientificSearchPipeline([provider])

        result = pipeline.execute({"query": "test"})

        self.assertEqual("scientific_search", result["pipeline"])
        self.assertEqual(["crossref"], result["providers"])
        self.assertEqual(1, result["count"])

    def test_unknown_provider_is_rejected(self):
        pipeline = ScientificSearchPipeline()
        with self.assertRaises(KeyError):
            pipeline.search("test", providers=["missing"])

    def test_duplicate_provider_is_rejected(self):
        provider = FakeProvider("crossref", [])
        pipeline = ScientificSearchPipeline([provider])
        with self.assertRaises(ValueError):
            pipeline.register_provider(provider)

    def test_invalid_provider_is_rejected(self):
        with self.assertRaises(TypeError):
            ScientificSearchPipeline([object()])


if __name__ == "__main__":
    unittest.main()
