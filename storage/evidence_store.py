class EvidenceStore:
    def __init__(self):
        # armazena evidências por IEC
        self.evidence_map = {}

    # -----------------------------
    # adicionar evidência
    # -----------------------------
    def add_evidence(self, iec_id, source, evidence_type="study", confidence=0.5):
        evidence = {
            "source": source,
            "type": evidence_type,
            "confidence": float(confidence)
        }

        if iec_id not in self.evidence_map:
            self.evidence_map[iec_id] = []

        self.evidence_map[iec_id].append(evidence)

    # -----------------------------
    # obter evidências de um IEC
    # -----------------------------
    def get_evidence(self, iec_id):
        return self.evidence_map.get(iec_id, [])

    # -----------------------------
    # calcular confiança média
    # -----------------------------
    def get_confidence(self, iec_id):
        evidences = self.get_evidence(iec_id)

        if not evidences:
            return 0.0

        total = sum(e["confidence"] for e in evidences)
        return total / len(evidences)

    # -----------------------------
    # listar tudo (debug)
    # -----------------------------
    def __repr__(self):
        return f"EvidenceStore(iec_count={len(self.evidence_map)})"