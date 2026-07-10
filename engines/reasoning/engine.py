class ReasoningEngine:
    """
    Motor inicial de raciocínio do KALATRACE.
    Trabalha em cima do KnowledgeGraph e IEC.
    """

    def __init__(self, graph):
        self.graph = graph

    # -----------------------------
    # 1. INFERÊNCIA SIMPLES
    # -----------------------------
    def infer_connections(self, node_id, threshold=0.5):
        """
        Sugere nós relacionados com base em conexões indiretas.
        """

        node = self.graph.get_node(node_id)
        if not node:
            return []

        neighbors = self.graph.neighbors(node_id)
        suggestions = set()

        for neighbor in neighbors:
            neighbor_id = neighbor.id

            # pega vizinhos dos vizinhos (2º grau)
            second_degree = self.graph.neighbors(neighbor_id)

            for candidate in second_degree:
                if candidate.id != node_id:
                    suggestions.add(candidate.id)

        # remove já conectados
        existing = {
            e["target"] if e["source"] == node_id else e["source"]
            for e in self.graph.edges_of(node_id)
        }

        return [
            self.graph.get_node(n)
            for n in suggestions
            if n not in existing
        ]

    # -----------------------------
    # 2. DETECÇÃO DE CONTRADIÇÃO
    # -----------------------------
    def detect_conflicts(self):
        """
        Detecta possíveis contradições com base em relações opostas.
        (versão inicial simples)
        """

        conflicts = []

        for edge in self.graph.edges:
            if edge["type"] == "supports":
                source = edge["source"]
                target = edge["target"]

                # procura se existe negação entre os mesmos nós
                for e in self.graph.edges:
                    if (
                        e["source"] == source and
                        e["target"] == target and
                        e["type"] == "contradicts"
                    ):
                        conflicts.append({
                            "source": source,
                            "target": target,
                            "issue": "support_vs_contradiction"
                        })

        return conflicts

    # -----------------------------
    # 3. PROPAGAÇÃO DE CONFIANÇA
    # -----------------------------
    def propagate_confidence(self, node_id, decay=0.9):
        """
        Propaga confiança de um nó para seus vizinhos.
        """

        node = self.graph.get_node(node_id)
        if not node:
            return {}

        neighbors = self.graph.neighbors(node_id)

        propagated = {}

        for neighbor in neighbors:
            influence = node.confidence * decay

            # média simples (pode evoluir depois)
            new_conf = (neighbor.confidence + influence) / 2

            neighbor.update_confidence(new_conf)

            propagated[neighbor.id] = new_conf

        return propagated

    # -----------------------------
    # 4. SUGESTÃO DE CONEXÕES
    # -----------------------------
    def suggest_edges(self, node_id, min_common=2):
        """
        Sugere novas conexões com base em vizinhos em comum.
        """

        neighbors = self.graph.neighbors(node_id)
        candidates = {}

        for neighbor in neighbors:
            for second in self.graph.neighbors(neighbor.id):
                if second.id == node_id:
                    continue

                candidates[second.id] = candidates.get(second.id, 0) + 1

        suggestions = [
            self.graph.get_node(nid)
            for nid, count in candidates.items()
            if count >= min_common
        ]

        return suggestions

    # -----------------------------
    # 5. RESUMO DO ESTADO COGNITIVO
    # -----------------------------
    def system_state(self):
        """
        Retorna visão geral do estado epistemológico do grafo.
        """

        return {
            "nodes": len(self.graph.nodes),
            "edges": len(self.graph.edges),
            "isolated": len(self.graph.isolated_nodes()),
            "low_confidence_edges": len(self.graph.low_confidence_edges()),
        }