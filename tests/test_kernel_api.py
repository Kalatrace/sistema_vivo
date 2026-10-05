import importlib
import unittest

from api import kernel


class KernelApiContractTests(unittest.TestCase):
    def setUp(self):
        importlib.reload(kernel)
        self.kernel = kernel
        self.EvidenceIn = self.kernel.EvidenceIn
        self.IECIn = self.kernel.IECIn
        self.KnowledgeStateIn = self.kernel.KnowledgeStateIn
        self.RelationIn = self.kernel.RelationIn
        self.ReliabilityIn = self.kernel.ReliabilityIn

    def test_health_is_canonical(self):
        self.assertEqual({"status": "ok", "kernel": "canonical"}, self.kernel.health())

    def test_vertical_api_contract(self):
        a = "api-a"
        b = "api-b"
        self.kernel.create_iec(self.IECIn(id=a, content="Conhecimento A", embedding=[1.0, 0.0]))
        self.kernel.create_iec(self.IECIn(id=b, content="Conhecimento B", embedding=[0.0, 1.0]))
        self.kernel.attach_evidence(a, self.EvidenceIn(evidence_id="api-evidence-a", content={"title": "Fonte A"}, source_type="scientific:test", reliability=0.9))
        self.kernel.attach_evidence(b, self.EvidenceIn(evidence_id="api-evidence-b", content={"title": "Fonte B"}, source_type="scientific:test", reliability=0.9))
        self.assertEqual("strong", self.kernel.validate(a)["status"])
        relation = self.kernel.promote_relation(self.RelationIn(source=a, target=b, evidence_ids=["api-evidence-a", "api-evidence-b"], relation_type="supports"))
        self.assertTrue(relation["promoted"])
        self.assertEqual(2, len(self.kernel.get_graph()["nodes"]))
        self.assertEqual(1, len(self.kernel.get_graph()["edges"]))
        self.assertEqual(2, self.kernel.status()["graph"]["nodes"])
        self.assertEqual(2, self.kernel.status()["evidence"]["total_evidences"])

    def test_curation_api_contract(self):
        gap_id = "api-curation-gap"
        self.kernel.create_iec(self.IECIn(id=gap_id, content="Nó isolado", embedding=[1.0, 0.0]))
        gaps = self.kernel.curation_gaps()
        self.assertIn(gap_id, [item["node_id"] for item in gaps["gaps"]])

        duplicate_id = "api-curation-duplicate"
        self.kernel.create_iec(self.IECIn(id=duplicate_id, content="Nó semelhante", embedding=[1.0, 0.0]))
        duplicates = self.kernel.curation_duplicates()
        self.assertTrue(any(
            {item["a"], item["b"]} == {gap_id, duplicate_id}
            for item in duplicates["duplicates"]
        ))

        reliability = self.kernel.curation_reliability(self.ReliabilityIn(factors={
            "methodological_quality": 1,
            "sample_size": 1,
            "bias_risk_inverted": 1,
            "reproducibility": 1,
            "statistical_consistency": 1,
            "recency": 1,
        }))
        self.assertEqual(100.0, reliability["score"])

        state = self.kernel.curation_knowledge_state(
            self.KnowledgeStateIn(maturity_score=90, reliability_score=95, has_active_conflict=True)
        )
        self.assertEqual("Conhecimento Contestado", state["state"])


if __name__ == "__main__":
    unittest.main()
