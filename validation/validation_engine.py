class ValidationEngine:
    """Valida a sustentação epistemológica do conhecimento no grafo."""

    def __init__(self, graph, evidence_store):
        self.graph = graph
        self.evidence_store = evidence_store

    def validate_iec(self, iec_id):
        evidence = self.evidence_store.get_evidence_for_iec(iec_id)
        if not evidence:
            return {
                "iec": iec_id,
                "status": "weak",
                "reason": "no_evidence",
                "confidence": 0.0,
                "evidence_count": 0,
            }

        avg_confidence = self.evidence_store.compute_evidence_strength(iec_id)

        if avg_confidence >= 0.75:
            status = "strong"
        elif avg_confidence >= 0.5:
            status = "moderate"
        else:
            status = "weak"

        return {
            "iec": iec_id,
            "status": status,
            "confidence": avg_confidence,
            "evidence_count": len(evidence),
        }

    def validate_edge(self, edge):
        source = edge["source"]
        target = edge["target"]
        source_val = self.validate_iec(source)
        target_val = self.validate_iec(target)
        confidence = (source_val["confidence"] + target_val["confidence"]) / 2
        weight = edge.get("weight", 0.5)
        final_score = (confidence + weight) / 2

        if final_score >= 0.75:
            status = "strong"
        elif final_score >= 0.5:
            status = "moderate"
        else:
            status = "weak"

        return {
            "source": source,
            "target": target,
            "relation_type": edge.get("type"),
            "status": status,
            "score": final_score,
        }

    def validate_graph(self):
        results = [self.validate_edge(edge) for edge in self.graph.edges]
        if not results:
            return {"status": "empty_graph", "score": 0.0, "evaluations": []}

        avg_score = sum(r["score"] for r in results) / len(results)
        if avg_score >= 0.75:
            status = "strong_knowledge_base"
        elif avg_score >= 0.5:
            status = "moderate_knowledge_base"
        else:
            status = "weak_knowledge_base"

        return {
            "status": status,
            "average_score": avg_score,
            "evaluations": results,
        }

    def validate_all(self):
        """Contrato oficial usado pelo LifecycleManager."""
        return self.validate_graph()

    def weak_nodes(self, threshold=0.5):
        weak = []
        for node_id in self.graph.nodes:
            validation = self.validate_iec(node_id)
            if validation["confidence"] < threshold:
                weak.append(validation)
        return weak

    def weak_knowledge(self, threshold=0.5):
        """Retorna IECs fracos para o ciclo de manutenção do Kernel."""
        return [
            self.graph.get_node(item["iec"])
            for item in self.weak_nodes(threshold=threshold)
            if self.graph.get_node(item["iec"]) is not None
        ]

    def report(self):
        """Relatório compacto de validação do estado atual."""
        validation = self.validate_all()
        return {
            "validation": validation,
            "weak_knowledge": len(self.weak_knowledge()),
            "graph": self.graph.stats(),
            "evidence": self.evidence_store.stats(),
        }

    def system_quality_score(self):
        """Score agregado do grafo, mantendo 0.0 para grafo sem relações."""
        validation = self.validate_all()
        return float(validation.get("average_score", validation.get("score", 0.0)))
