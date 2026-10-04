import unittest

from engines.scientific_research.evidence import ScientificEvidenceBridge


class ScientificEvidenceBridgeTests(unittest.TestCase):
    def test_stable_identifier(self):
        result = {"provider": "crossref", "doi": "10.1/a"}
        self.assertEqual(
            ScientificEvidenceBridge.evidence_id(result),
            ScientificEvidenceBridge.evidence_id(dict(result)),
        )


if __name__ == "__main__":
    unittest.main()
