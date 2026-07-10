class CuriosityEngine:
    def __init__(self, graph, evidence_store, validator):
        self.graph = graph
        self.evidence_store = evidence_store
        self.validator = validator

    # -----------------------------
    # 1. nós isolados
    # -----------------------------
    def find_isolated_nodes(self):
        connected = set()

        for edge in self.graph.edges:
            connected.add(edge["source"])
            connected.add(edge["target"])

        return [
            node_id for node_id in self.graph.nodes
            if node_id not in connected
        ]

    # -----------------------------
    # 2. fator de evidência (0 = fraco, 1 = forte)
    # -----------------------------
    def _evidence_factor(self, iec_id):
        return self.evidence_store.get_confidence(iec_id)

    # -----------------------------
    # 3. fator de validação estrutural
    # -----------------------------
    def _validation_factor(self, iec_id):
        val = self.validator.validate_iec(iec_id)

        # strong = bom (baixa curiosidade)
        # weak = ruim (alta curiosidade)
        status = val["status"]

        if status == "strong":
            return 0.0
        elif status == "moderate":
            return 0.5
        else:
            return 1.0

    # -----------------------------
    # 4. fator de isolamento
    # -----------------------------
    def _isolation_factor(self, iec_id):
        return 1.0 if iec_id in self.find_isolated_nodes() else 0.0

    # -----------------------------
    # 5. fator de conectividade (grau do nó)
    # -----------------------------
    def _connectivity_factor(self, iec_id):
        degree = 0

        for edge in self.graph.edges:
            if edge["source"] == iec_id or edge["target"] == iec_id:
                degree += 1

        # menos conexões = mais curioso
        return 1 / (degree + 1)

    # -----------------------------
    # 6. score final de curiosidade
    # -----------------------------
    def curiosity_score(self, iec_id):
        evidence = self._evidence_factor(iec_id)
        validation = self._validation_factor(iec_id)
        isolation = self._isolation_factor(iec_id)
        connectivity = self._connectivity_factor(iec_id)

        # fórmula equilibrada (0 → 1)
        score = (
            (1 - evidence) * 0.35 +
            validation * 0.30 +
            isolation * 0.20 +
            connectivity * 0.15
        )

        return {
            "iec": iec_id,
            "curiosity_score": round(score, 4),
            "evidence_factor": round(evidence, 3),
            "validation_factor": round(validation, 3),
            "isolation_factor": isolation,
            "connectivity_factor": round(connectivity, 3)
        }

    # -----------------------------
    # 7. ranking geral
    # -----------------------------
    def rank_curiosity(self):
        results = []

        for node_id in self.graph.nodes:
            results.append(self.curiosity_score(node_id))

        return sorted(results, key=lambda x: x["curiosity_score"], reverse=True)

    # -----------------------------
    # 8. sugestão de exploração
    # -----------------------------
    def suggest_next_exploration(self, top_n=3):
        return self.rank_curiosity()[:top_n]