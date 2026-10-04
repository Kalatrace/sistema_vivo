import unittest

from agents.research_agent import ResearchAgent
from engines.scientific_research import ScientificResearchEngine


class ResearchAgentTests(unittest.TestCase):
    def setUp(self):
        self.engine = ScientificResearchEngine(
            {"mock": lambda query: [{"title": "Study A"}, {"title": "Study B"}]}
        )
        self.agent = ResearchAgent(self.engine)

    def test_search_delegates_to_engine(self):
        result = self.agent.run({"query": "skin regeneration"})
        self.assertEqual(result["agent"], "research")
        self.assertEqual(result["action"], "search")
        self.assertEqual(result["count"], 2)
        self.assertEqual(result["result"][0]["provider"], "mock")

    def test_execute_action_delegates_to_engine(self):
        result = self.agent.run(
            {"action": "execute", "query": "knowledge graphs", "provider": "mock"}
        )
        self.assertEqual(result["result"]["engine"], "scientific_research")
        self.assertEqual(result["result"]["count"], 2)

    def test_unknown_action_is_rejected(self):
        with self.assertRaises(ValueError):
            self.agent.run({"action": "unsupported", "query": "x"})

    def test_engine_is_required(self):
        with self.assertRaises(ValueError):
            ResearchAgent(None)


if __name__ == "__main__":
    unittest.main()
