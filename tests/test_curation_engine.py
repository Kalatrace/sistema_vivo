import unittest

from engines.curation import CurationEngine
from graph.knowledge_graph import KnowledgeGraph
from knowledge.iec import IEC


class CurationEngineTests(unittest.TestCase):
    def setUp(self):
        self.graph = KnowledgeGraph()
        self.engine = CurationEngine(self.graph)

    def test_gap_detection_uses_graph_isolation(self):
        self.graph.add_node(IEC(id="a", content="A", embedding=[1.0, 0.0], node_type="Hipótese"))
        gaps = self.engine.detect_gaps()
        self.assertEqual(["a"], [item["node_id"] for item in gaps])

    def test_duplicate_detection_is_candidate_only(self):
        self.graph.add_node(IEC(id="a", content="A", embedding=[1.0, 0.0]))
        self.graph.add_node(IEC(id="b", content="B", embedding=[1.0, 0.0]))
        duplicates = self.engine.detect_duplicates()
        self.assertEqual([("a", "b")], [(item["a"], item["b"]) for item in duplicates])
        self.assertEqual(0, len(self.graph.edges))

    def test_reliability_score_preserves_blueprint_weights(self):
        factors = {
            "methodological_quality": 1,
            "sample_size": 1,
            "bias_risk_inverted": 1,
            "reproducibility": 1,
            "statistical_consistency": 1,
            "recency": 1,
        }
        self.assertEqual(100.0, CurationEngine.reliability_score(factors))

    def test_knowledge_state_preserves_conflict(self):
        self.assertEqual(
            "Conhecimento Contestado",
            CurationEngine.classify_knowledge_state(90, 95, has_active_conflict=True),
        )
        self.assertEqual(
            "Conhecimento Consolidado",
            CurationEngine.classify_knowledge_state(90, 95),
        )


if __name__ == "__main__":
    unittest.main()
