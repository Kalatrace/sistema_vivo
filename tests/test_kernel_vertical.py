"""Teste vertical do Kernel com componentes reais, sem persistência externa."""
import unittest

from core.lifecycle_manager import LifecycleManager
from engines.reasoning.engine import ReasoningEngine
from graph.knowledge_graph import KnowledgeGraph
from knowledge.iec import IEC
from memory.evidence_store import EvidenceStore
from validation.validation_engine import ValidationEngine


class KernelVerticalTests(unittest.TestCase):
    def setUp(self):
        self.graph = KnowledgeGraph()
        self.evidence = EvidenceStore()
        self.validator = ValidationEngine(self.graph, self.evidence)
        self.reasoner = ReasoningEngine(self.graph)
        self.lifecycle = LifecycleManager(
            self.graph, self.evidence, self.validator, self.reasoner
        )

    def test_create_support_validate_and_reason(self):
        a = IEC("iec-a", "Conhecimento A", embedding=[1.0, 0.0])
        b = IEC("iec-b", "Conhecimento B", embedding=[0.0, 1.0])
        c = IEC("iec-c", "Conhecimento C", embedding=[1.0, 0.0])

        self.lifecycle.create_iec(a)
        self.lifecycle.create_iec(b)
        self.lifecycle.create_iec(c)

        self.lifecycle.attach_evidence(
            "iec-a", "ev-a", "Fonte de suporte A", reliability=0.9
        )
        self.lifecycle.attach_evidence(
            "iec-b", "ev-b", "Fonte de suporte B", reliability=0.7
        )

        self.lifecycle.connect("iec-a", "iec-b")
        self.lifecycle.connect("iec-b", "iec-c")

        validation = self.lifecycle.validate("iec-a")
        self.assertEqual(validation["status"], "strong")
        self.assertEqual(validation["evidence_count"], 1)

        inferred = self.lifecycle.reason("iec-a")
        self.assertEqual([item.id for item in inferred], ["iec-c"])

        status = self.lifecycle.status()
        self.assertEqual(status["graph"]["nodes"], 3)
        self.assertEqual(status["graph"]["edges"], 2)
        self.assertEqual(status["evidence"]["total_evidences"], 2)

    def test_missing_iec_validation_is_safe(self):
        result = self.lifecycle.validate("not-found")
        self.assertEqual(result["status"], "weak")
        self.assertEqual(result["reason"], "no_evidence")
        self.assertEqual(result["evidence_count"], 0)

    def test_evidence_can_support_multiple_knowledge_items(self):
        self.evidence.add_evidence("shared", "Evidência compartilhada", reliability=0.8)
        self.evidence.link_to_iec("shared", "iec-x")
        self.evidence.link_to_iec("shared", "iec-y")
        self.assertEqual(len(self.evidence.get_evidence_for_iec("iec-x")), 1)
        self.assertEqual(len(self.evidence.get_evidence_for_iec("iec-y")), 1)


if __name__ == "__main__":
    unittest.main()
