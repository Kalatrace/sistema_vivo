import unittest

from core.lifecycle_manager import LifecycleManager
from engines.reasoning.engine import ReasoningEngine
from graph.knowledge_graph import KnowledgeGraph
from knowledge.iec import IEC
from memory.evidence_store import EvidenceStore
from validation.validation_engine import ValidationEngine


class ReasoningEvidenceTests(unittest.TestCase):
    def test_shared_evidence_is_only_a_suggestion(self):
        graph = KnowledgeGraph()
        store = EvidenceStore()
        graph.add_node(IEC(id="iec-a", content="A", embedding=[1.0, 0.0]))
        graph.add_node(IEC(id="iec-b", content="B", embedding=[0.0, 1.0]))
        store.add_evidence("ev-1", {"title": "Paper"}, source_type="scientific:crossref", reliability=0.9)
        store.link_to_iec("ev-1", "iec-a")
        store.link_to_iec("ev-1", "iec-b")
        suggestions = ReasoningEngine(graph, evidence_store=store).infer_evidence_connections("iec-a")
        self.assertEqual([{"node_id": "iec-b", "shared_evidence": ["ev-1"]}], suggestions)
        self.assertEqual(0, len(graph.edges))

    def test_without_evidence_store_contract_remains_safe(self):
        graph = KnowledgeGraph()
        graph.add_node(IEC(id="iec-a", content="A", embedding=[1.0, 0.0]))
        self.assertEqual([], ReasoningEngine(graph).infer_evidence_connections("iec-a"))


class RelationPromotionTests(unittest.TestCase):
    def setUp(self):
        self.graph = KnowledgeGraph()
        self.store = EvidenceStore()
        self.validator = ValidationEngine(self.graph, self.store)
        self.reasoner = ReasoningEngine(self.graph, self.store)
        self.lifecycle = LifecycleManager(self.graph, self.store, self.validator, self.reasoner)
        self.graph.add_node(IEC(id="a", content="A", embedding=[1.0, 0.0]))
        self.graph.add_node(IEC(id="b", content="B", embedding=[0.0, 1.0]))

    def test_strong_evidence_promotes_relation(self):
        self.store.add_evidence("ev", {"title": "Paper"}, source_type="scientific:crossref", reliability=0.9)
        self.store.link_to_iec("ev", "a")
        self.store.link_to_iec("ev", "b")
        result = self.lifecycle.promote_relation("a", "b", ["ev"], relation_type="supports")
        self.assertTrue(result["promoted"])
        self.assertEqual(1, len(self.graph.edges))
        self.assertEqual(["ev"], self.graph.edges[0]["evidence"])
        self.assertEqual(0.9, self.graph.edges[0]["confidence"])

    def test_weak_evidence_does_not_promote_relation(self):
        self.store.add_evidence("ev", {"title": "Weak"}, source_type="scientific:crossref", reliability=0.4)
        self.store.link_to_iec("ev", "a")
        self.store.link_to_iec("ev", "b")
        result = self.lifecycle.promote_relation("a", "b", ["ev"])
        self.assertFalse(result["promoted"])
        self.assertEqual("insufficient_support", result["decision"]["reason"])
        self.assertEqual(0, len(self.graph.edges))

    def test_conflicting_relation_preserves_both_evidence_sides(self):
        for evidence_id in ("support", "contradiction"):
            self.store.add_evidence(evidence_id, {"title": evidence_id}, source_type="scientific:crossref", reliability=0.9)
            self.store.link_to_iec(evidence_id, "a")
            self.store.link_to_iec(evidence_id, "b")
        first = self.lifecycle.promote_relation("a", "b", ["support"], relation_type="supports")
        second = self.lifecycle.promote_relation("a", "b", ["contradiction"], relation_type="contradicts")
        self.assertTrue(first["promoted"])
        self.assertTrue(second["promoted"])
        self.assertEqual("conflicted", second["decision"]["status"])
        self.assertEqual(["contradiction"], second["decision"]["conflict"]["candidate_evidence"])
        self.assertEqual(["support"], second["decision"]["conflict"]["support_evidence"])
        self.assertEqual([], second["decision"]["conflict"]["contradiction_evidence"])
        self.assertEqual(2, len(self.graph.edges))

    def test_missing_evidence_is_rejected(self):
        result = self.lifecycle.promote_relation("a", "b", ["missing"])
        self.assertFalse(result["promoted"])
        self.assertEqual("missing_evidence", result["decision"]["reason"])
        self.assertEqual(0, len(self.graph.edges))


if __name__ == "__main__":
    unittest.main()
