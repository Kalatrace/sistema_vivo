class EvidenceStore:
    """
    Armazena e gerencia evidências do sistema KALATRACE.
    Cada evidência pode sustentar um ou mais IECs.
    """

    def __init__(self):
        # estrutura principal: evidências por id
        self.evidences = {}

        # índice reverso: IEC -> evidências
        self.iec_index = {}

    # -----------------------------
    # 1. ADICIONAR EVIDÊNCIA
    # -----------------------------
    def add_evidence(self, evidence_id, content, source_type="unknown", reliability=0.5):
        """
        Registra uma nova evidência no sistema.
        """

        self.evidences[evidence_id] = {
            "id": evidence_id,
            "content": content,
            "source_type": source_type,
            "reliability": float(reliability),
            "linked_iec": set(),
        }

    # -----------------------------
    # 2. LIGAR EVIDÊNCIA A IEC
    # -----------------------------
    def link_to_iec(self, evidence_id, iec_id):
        """
        Conecta uma evidência a um IEC específico.
        """

        if evidence_id not in self.evidences:
            raise ValueError(f"Evidência {evidence_id} não existe")

        self.evidences[evidence_id]["linked_iec"].add(iec_id)

        if iec_id not in self.iec_index:
            self.iec_index[iec_id] = set()

        self.iec_index[iec_id].add(evidence_id)

    # -----------------------------
    # 3. RECUPERAR EVIDÊNCIAS DE UM IEC
    # -----------------------------
    def get_evidence_for_iec(self, iec_id):
        """
        Retorna todas as evidências associadas a um IEC.
        """

        evidence_ids = self.iec_index.get(iec_id, set())

        return [
            self.evidences[eid]
            for eid in evidence_ids
            if eid in self.evidences
        ]

    # -----------------------------
    # 4. CALCULAR FORÇA DE EVIDÊNCIA
    # -----------------------------
    def compute_evidence_strength(self, iec_id):
        """
        Calcula força agregada das evidências de um IEC.
        """

        evidences = self.get_evidence_for_iec(iec_id)

        if not evidences:
            return 0.0

        total = sum(e["reliability"] for e in evidences)

        return total / len(evidences)

    # -----------------------------
    # 5. REMOVER EVIDÊNCIA
    # -----------------------------
    def remove_evidence(self, evidence_id):
        """
        Remove evidência e suas conexões.
        """

        if evidence_id not in self.evidences:
            return

        linked = self.evidences[evidence_id]["linked_iec"]

        for iec_id in linked:
            if iec_id in self.iec_index:
                self.iec_index[iec_id].discard(evidence_id)

        del self.evidences[evidence_id]

    # -----------------------------
    # 6. ESTADO DO SISTEMA
    # -----------------------------
    def stats(self):
        return {
            "total_evidences": len(self.evidences),
            "linked_iec": len(self.iec_index),
        }

    # -----------------------------
    # 7. DEBUG
    # -----------------------------
    def __repr__(self):
        s = self.stats()
        return (
            f"EvidenceStore("
            f"evidences={s['total_evidences']}, "
            f"linked_iec={s['linked_iec']}"
            f")"
        )