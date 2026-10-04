import unittest

from engines.reasoning.engine import ReasoningEngine
from graph.knowledge_graph import KnowledgeGraph
from knowledge.iec import IEC
from memory.evidence_store import EvidenceStore


class ReasoningEvidenceTests(unittest.TestCase):
    def test_shared_evidence_is_only_a_suggestion(self):
        graph = KnowledgeGraph()
        store = EvidenceStore()
        first = IEC(id="iec-a", content="A", embedding=[1.0, 0.0])
        second = IEC(id="iec-b", content="B", embedding=[0.0, 1.0])
        graph.add_node(first)
        graph.add_node(second)

        store.add_evidence("ev-1", {"title": "Paper"}, source_type="scientific:crossref", reliability=0.9)
        store.link_to_iec("ev-1", first.id)
        store.link_to_iec("ev-1", second.id)

        engine = ReasoningEngine(graph, evidence_store=store)
        suggestions = engine.infer_evidence_connections(first.id)

        self.assertEqual([{"node_id": "iec-b", "shared_evidence": ["ev-1"]}], suggestions)
        self.assertEqual(0, len(graph.edges))

    def test_without_evidence_store_contract_remains_safe(self):
        graph = KnowledgeGraph()
        graph.add_node(IEC(id="iec-a", content="A", embedding=[1.0, 0.0]))
        self.assertEqual([], ReasoningEngine(graph).infer_evidence_connections("iec-a"))


if __name__ == "__main__":
    unittest.main()
