import unittest

from engines.scientific_research import ScientificResearchEngine


class ScientificResearchEngineTests(unittest.TestCase):
    def setUp(self):
        self.engine = ScientificResearchEngine({
            "mock": lambda query: [
                {"title": "Study A", "doi": "10.1000/a"},
                {"title": "Study B"},
            ]
        })

    def test_search_normalizes_provider_and_query(self):
        results = self.engine.search("skin regeneration")
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["provider"], "mock")
        self.assertEqual(results[0]["query"], "skin regeneration")

    def test_execute_returns_stable_envelope(self):
        result = self.engine.execute({"query": "knowledge graphs", "provider": "mock"})
        self.assertEqual(result["engine"], "scientific_research")
        self.assertEqual(result["count"], 2)

    def test_unknown_provider_is_rejected(self):
        with self.assertRaises(KeyError):
            self.engine.search("query", provider="missing")

    def test_empty_query_is_rejected(self):
        with self.assertRaises(ValueError):
            self.engine.search("")

    def test_provider_contract_is_checked(self):
        with self.assertRaises(TypeError):
            self.engine.register_provider("bad", object())


if __name__ == "__main__":
    unittest.main()
