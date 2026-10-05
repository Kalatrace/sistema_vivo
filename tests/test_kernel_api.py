import unittest

from api import kernel
from api.kernel import EvidenceIn, IECIn, KnowledgeStateIn, RelationIn, ReliabilityIn


class KernelApiContractTests(unittest.TestCase):
    def test_health_is_canonical(self):
        self.assertEqual({"status": "ok", "kernel": "canonical"}, kernel.health())

    def test_vertical_api_contract(self):
        a = "api-a"
        b = "api-b"
        kernel.create_iec(IECIn(id=a, content="Conhecimento A", embedding=[1.0, 0.0]))
        kernel.create_iec(IECIn(id=b, content="Conhecimento B", embedding=[0.0, 1.0]))
        kernel.attach_evidence(a, EvidenceIn(evidence_id="api-evidence-a", content={"title": "Fonte A"}, source_type="scientific:test", reliability=0.9))
        kernel.attach_evidence(b, EvidenceIn(evidence_id="api-evidence-b", content={"title": "Fonte B"}, source_type="scientific:test", reliability=0.9))
        self.assertEqual("strong", kernel.validate(a)["status"])
        relation = kernel.promote_relation(RelationIn(source=a, target=b, evidence_ids=["api-evidence-a", "api-evidence-b"], relation_type="supports"))
        self.assertTrue(relation["promoted"])
        self.assertEqual(2, len(kernel.get_graph()["nodes"]))
        self.assertEqual(1, len(kernel.get_graph()["edges"]))
        self.assertEqual(2, kernel.status()["graph"]["nodes"])
        self.assertEqual(2, kernel.status()["evidence"]["total_evidences"])

    def test_curation_api_contract(self):
        gap_id = "api-curation-gap"
        kernel.create_iec(IECIn(id=gap_id, content="Nó isolado", embedding=[1.0, 0.0]))
        gaps = kernel.curation_gaps()
        self.assertIn(gap_id, [item["node_id"] for item in gaps["gaps"]])

        duplicate_id = "api-curation-duplicate"
        kernel.create_iec(IECIn(id=duplicate_id, content="Nó semelhante", embedding=[1.0, 0.0]))
        duplicates = kernel.curation_duplicates()
        self.assertTrue(any(
            {item["a"], item["b"]} == {gap_id, duplicate_id}
            for item in duplicates["duplicates"]
        ))

        reliability = kernel.curation_reliability(ReliabilityIn(factors={
            "methodological_quality": 1,
            "sample_size": 1,
            "bias_risk_inverted": 1,
            "reproducibility": 1,
            "statistical_consistency": 1,
            "recency": 1,
        }))
        self.assertEqual(100.0, reliability["score"])

        state = kernel.curation_knowledge_state(
            KnowledgeStateIn(maturity_score=90, reliability_score=95, has_active_conflict=True)
        )
        self.assertEqual("Conhecimento Contestado", state["state"])


if __name__ == "__main__":
    unittest.main()
