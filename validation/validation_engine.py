class ValidationEngine:
    def __init__(self, graph, evidence_store):
        """
        graph: KnowledgeGraph
        evidence_store: EvidenceStore
        """
        self.graph = graph
        self.evidence_store = evidence_store

    # -----------------------------
    # 1. validar um IEC individual
    # -----------------------------
    def validate_iec(self, iec_id):
        evidence = self.evidence_store.get_evidence(iec_id)

        if not evidence:
            return {
                "iec": iec_id,
                "status": "weak",
                "reason": "no_evidence",
                "confidence": 0.0
            }

        avg_confidence = self.evidence_store.get_confidence(iec_id)

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
            "evidence_count": len(evidence)
        }

    # -----------------------------
    # 2. validar uma relação (edge)
    # -----------------------------
    def validate_edge(self, edge):
        source = edge["source"]
        target = edge["target"]

        source_val = self.validate_iec(source)
        target_val = self.validate_iec(target)

        # média simples de confiança
        confidence = (source_val["confidence"] + target_val["confidence"]) / 2

        # peso estrutural da relação
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
            "score": final_score
        }

    # -----------------------------
    # 3. validar o grafo inteiro
    # -----------------------------
    def validate_graph(self):
        results = []

        for edge in self.graph.edges:
            results.append(self.validate_edge(edge))

        if not results:
            return {
                "status": "empty_graph",
                "score": 0.0
            }

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
            "evaluations": results
        }

    # -----------------------------
    # 4. detectar IECs fracos
    # -----------------------------
    def weak_nodes(self, threshold=0.5):
        weak = []

        for node_id in self.graph.nodes:
            val = self.validate_iec(node_id)
            if val["confidence"] < threshold:
                weak.append(val)

        return weak