import unittest

from engines.scientific_research.evidence import ScientificEvidenceBridge
from graph.knowledge_graph import KnowledgeGraph
from knowledge.iec import IEC
from memory.evidence_store import EvidenceStore


class ScientificEvidenceBridgeTests(unittest.TestCase):
    def test_ingest_preserves_provenance_and_links_iec(self):
        store = EvidenceStore()
        bridge = ScientificEvidenceBridge(store)
        result = {
            "provider": "crossref",
            "query": "skin regeneration",
            "title": "Paper A",
            "doi": "10.1/a",
        }

        evidence_id = bridge.ingest("iec-research", result, reliability=0.9)
        evidence = store.get_evidence_for_iec("iec-research")[0]

        self.assertEqual(evidence_id, evidence["id"])
        self.assertEqual("scientific:crossref", evidence["source_type"])
        self.assertEqual(0.9, evidence["reliability"])
        self.assertEqual("10.1/a", evidence["content"]["doi"])

    def test_stable_identifier(self):
        result = {"provider": "pubmed", "pmid": "123", "title": "Paper"}
        self.assertEqual(
            ScientificEvidenceBridge.evidence_id(result),
            ScientificEvidenceBridge.evidence_id(dict(result)),
        )

    def test_vertical_research_to_kernel_flow(self):
        graph = KnowledgeGraph()
        store = EvidenceStore()
        bridge = ScientificEvidenceBridge(store)
        iec = IEC(
            id="iec-vertical",
            content="Pesquisa incorporada",
            embedding=[1.0, 0.0],
        )
        graph.add_node(iec)

        results = [
            {
                "provider": "crossref",
                "query": "test",
                "title": "Paper A",
                "doi": "10.1/a",
            },
            {
                "provider": "pubmed",
                "query": "test",
                "title": "Paper B",
                "pmid": "2",
            },
        ]

        evidence_ids = bridge.ingest_many(iec.id, results, reliability=0.9)

        self.assertEqual(2, len(evidence_ids))
        self.assertEqual(2, len(store.get_evidence_for_iec(iec.id)))
        self.assertEqual(0.9, store.compute_evidence_strength(iec.id))
        self.assertEqual(1, graph.stats()["nodes"])


if __name__ == "__main__":
    unittest.main()
