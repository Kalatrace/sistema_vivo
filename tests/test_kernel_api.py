import unittest

from api import kernel
from api.kernel import EvidenceIn, IECIn, RelationIn


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


if __name__ == "__main__":
    unittest.main()
