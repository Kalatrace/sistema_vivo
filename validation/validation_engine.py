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

    def evaluate_edge_candidate(self, source, target, evidence_ids, weight=1.0, threshold=0.75):
        """Avalia uma relação candidata antes de permitir sua promoção ao grafo."""
        if not source or not target:
            raise ValueError("source e target são obrigatórios")
        if source == target:
            return {"eligible": False, "reason": "self_relation", "score": 0.0}
        if source not in self.graph.nodes or target not in self.graph.nodes:
            return {"eligible": False, "reason": "missing_iec", "score": 0.0}

        evidence_ids = list(evidence_ids or [])
        if not evidence_ids:
            return {"eligible": False, "reason": "no_evidence", "score": 0.0}

        available = {item["id"]: item for item in self.evidence_store.get_evidence_for_iec(source)}
        target_available = {item["id"]: item for item in self.evidence_store.get_evidence_for_iec(target)}
        evidence = []
        for evidence_id in evidence_ids:
            item = available.get(evidence_id) or target_available.get(evidence_id)
            if item is None:
                return {"eligible": False, "reason": "missing_evidence", "evidence_id": evidence_id, "score": 0.0}
            evidence.append(item)

        source_val = self.validate_iec(source)
        target_val = self.validate_iec(target)
        evidence_strength = sum(item["reliability"] for item in evidence) / len(evidence)
        node_support = (source_val["confidence"] + target_val["confidence"]) / 2
        score = (node_support + evidence_strength) / 2

        return {
            "eligible": score >= threshold,
            "reason": "validated" if score >= threshold else "insufficient_support",
            "source": source,
            "target": target,
            "evidence_ids": evidence_ids,
            "evidence_strength": evidence_strength,
            "node_support": node_support,
            "score": score,
            "threshold": threshold,
        }

    def evaluate_relation_conflict(self, source, target):
        """Descreve evidências divergentes sem apagar nenhum dos lados."""
        relations = [
            edge for edge in self.graph.edges
            if {edge["source"], edge["target"]} == {source, target}
        ]
        supports = [edge for edge in relations if edge.get("type") == "supports"]
        contradicts = [edge for edge in relations if edge.get("type") == "contradicts"]
        support_evidence = sorted({eid for edge in supports for eid in edge.get("evidence", [])})
        contradiction_evidence = sorted({eid for edge in contradicts for eid in edge.get("evidence", [])})
        conflict = bool(supports and contradicts)
        return {
            "source": source,
            "target": target,
            "conflict": conflict,
            "supports": len(supports),
            "contradicts": len(contradicts),
            "support_evidence": support_evidence,
            "contradiction_evidence": contradiction_evidence,
            "status": "conflicted" if conflict else "consistent",
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
