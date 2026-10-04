class EvidenceStore:
    """Armazena evidências e o índice reverso por IEC."""

    def __init__(self):
        self.evidences = {}
        self.iec_index = {}

    def add_evidence(self, evidence_id, content, source_type="unknown", reliability=0.5, provenance=None):
        self.evidences[evidence_id] = {
            "id": evidence_id, "content": content, "source_type": source_type,
            "reliability": float(reliability), "provenance": dict(provenance or {}),
            "linked_iec": set(),
        }

    def link_to_iec(self, evidence_id, iec_id):
        if evidence_id not in self.evidences:
            raise ValueError(f"Evidência {evidence_id} não existe")
        self.evidences[evidence_id]["linked_iec"].add(iec_id)
        self.iec_index.setdefault(iec_id, set()).add(evidence_id)

    def get_evidence_for_iec(self, iec_id):
        evidence_ids = self.iec_index.get(iec_id, set())
        return [self.evidences[eid] for eid in evidence_ids if eid in self.evidences]

    def compute_evidence_strength(self, iec_id):
        evidences = self.get_evidence_for_iec(iec_id)
        if not evidences:
            return 0.0
        return sum(e["reliability"] for e in evidences) / len(evidences)

    def remove_evidence(self, evidence_id):
        if evidence_id not in self.evidences:
            return
        for iec_id in self.evidences[evidence_id]["linked_iec"]:
            if iec_id in self.iec_index:
                self.iec_index[iec_id].discard(evidence_id)
        del self.evidences[evidence_id]

    def stats(self):
        return {"total_evidences": len(self.evidences), "linked_iec": len(self.iec_index)}

    def __repr__(self):
        s = self.stats()
        return f"EvidenceStore(evidences={s['total_evidences']}, linked_iec={s['linked_iec']})"
