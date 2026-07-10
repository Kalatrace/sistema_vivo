class ValidationEngine:
    """
    Motor de validação epistemológica do KALATRACE.

    Responsável por avaliar a confiabilidade dos IECs
    com base em evidências e estrutura do grafo.
    """

    def __init__(self, graph, evidence_store):
        self.graph = graph
        self.evidence_store = evidence_store

    # -----------------------------
    # 1. VALIDAR UM IEC INDIVIDUAL
    # -----------------------------
    def validate_iec(self, iec_id):
        """
        Calcula nova confiança do IEC com base em evidências.
        """

        iec = self.graph.get_node(iec_id)
        if not iec:
            return None

        evidence_strength = self.evidence_store.compute_evidence_strength(iec_id)

        # média entre confiança atual e força de evidência
        new_confidence = (iec.confidence + evidence_strength) / 2

        iec.update_confidence(new_confidence)

        return {
            "iec_id": iec_id,
            "old_confidence": iec.confidence,
            "evidence_strength": evidence_strength,
            "new_confidence": new_confidence,
        }

    # -----------------------------
    # 2. VALIDAR TODO O SISTEMA
    # -----------------------------
    def validate_all(self):
        """
        Revalida todos os IECs do grafo.
        """

        results = []

        for iec_id in self.graph.nodes:
            result = self.validate_iec(iec_id)
            if result:
                results.append(result)

        return results

    # -----------------------------
    # 3. DETECTAR CONHECIMENTO FRACO
    # -----------------------------
    def weak_knowledge(self, threshold=0.3):
        """
        Retorna IECs com baixa confiança.
        """

        weak = []

        for iec_id, iec in self.graph.nodes.items():
            if iec.confidence < threshold:
                weak.append(iec)

        return weak

    # -----------------------------
    # 4. DETECTAR CONTRADIÇÕES SIMPLES
    # -----------------------------
    def detect_basic_conflicts(self):
        """
        Detecta conflitos estruturais básicos no grafo.
        """

        conflicts = []

        for edge in self.graph.edges:
            if edge["type"] == "supports":
                source = edge["source"]
                target = edge["target"]

                for e in self.graph.edges:
                    if (
                        e["source"] == source
                        and e["target"] == target
                        and e["type"] == "contradicts"
                    ):
                        conflicts.append({
                            "source": source,
                            "target": target,
                            "issue": "support_vs_contradiction"
                        })

        return conflicts

    # -----------------------------
    # 5. SCORE GLOBAL DO SISTEMA
    # -----------------------------
    def system_quality_score(self):
        """
        Métrica geral de qualidade epistemológica do sistema.
        """

        nodes = self.graph.nodes.values()

        if not nodes:
            return 0.0

        avg_confidence = sum(n.confidence for n in nodes) / len(nodes)

        isolated_penalty = len(self.graph.isolated_nodes()) * 0.01

        return max(0.0, avg_confidence - isolated_penalty)

    # -----------------------------
    # 6. RELATÓRIO GERAL
    # -----------------------------
    def report(self):
        """
        Relatório completo de saúde do sistema.
        """

        return {
            "system_score": self.system_quality_score(),
            "weak_knowledge": len(self.weak_knowledge()),
            "conflicts": len(self.detect_basic_conflicts()),
            "total_nodes": len(self.graph.nodes),
            "total_edges": len(self.graph.edges),
        }