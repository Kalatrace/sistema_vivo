"""Engine canônico de curadoria do conhecimento.

A curadoria identifica candidatos para revisão; não apaga conhecimento nem
resolve conflitos científicos automaticamente.
"""

from utils.embeddings import cosine_similarity


class CurationEngine:
    def __init__(self, graph):
        if graph is None:
            raise ValueError("CurationEngine requer um KnowledgeGraph")
        self.graph = graph

    def detect_gaps(self):
        return [
            {
                "node_id": node.id,
                "node_type": node.node_type,
                "content": node.content,
                "message": "Poucas evidências conectando este nó ao restante do grafo.",
            }
            for node in self.graph.isolated_nodes()
        ]

    def detect_duplicates(self, threshold=0.92):
        pairs = []
        ids = list(self.graph.nodes)
        for i, left_id in enumerate(ids):
            for right_id in ids[i + 1:]:
                left = self.graph.nodes[left_id]
                right = self.graph.nodes[right_id]
                similarity = cosine_similarity(left.embedding, right.embedding)
                if similarity >= threshold:
                    pairs.append({
                        "a": left.id,
                        "b": right.id,
                        "similarity": round(similarity, 3),
                    })
        return pairs

    @staticmethod
    def reliability_score(factors, weights=None):
        default_weights = {
            "methodological_quality": 0.25,
            "sample_size": 0.15,
            "bias_risk_inverted": 0.20,
            "reproducibility": 0.20,
            "statistical_consistency": 0.10,
            "recency": 0.10,
        }
        weights = weights or default_weights
        total_weight = sum(weights.values())
        if total_weight <= 0:
            raise ValueError("Os pesos devem possuir soma positiva")
        score = 0.0
        for key, weight in weights.items():
            value = max(0.0, min(1.0, float(factors.get(key, 0.0))))
            score += value * weight
        return round((score / total_weight) * 100, 1)

    @staticmethod
    def classify_knowledge_state(
        maturity_score, reliability_score_value, has_active_conflict=False, superseded_by=None
    ):
        if superseded_by:
            return "Conhecimento Obsoleto"
        if has_active_conflict:
            return "Conhecimento Contestado"
        if maturity_score <= 20:
            return "Hipótese"
        if maturity_score <= 40:
            return "Evidência Emergente"
        if maturity_score <= 60 or reliability_score_value < 60:
            return "Conhecimento Moderado"
        return "Conhecimento Consolidado"
