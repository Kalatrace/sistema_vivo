from utils.embeddings import cosine_similarity


class ReasoningEngine:
    """
    Motor de raciocínio do KALATRACE.

    Mantém duas formas complementares de inferência:
    - estrutural: relações indiretas no KnowledgeGraph;
    - semântica: similaridade entre embeddings dos IECs.

    A inferência semântica não substitui a inferência do grafo. Ela fornece
    evidência adicional para uma futura camada de decisão/validação.
    """

    def __init__(self, graph, evidence_store=None):
        self.graph = graph
        self.evidence_store = evidence_store

    # -----------------------------
    # 1. INFERÊNCIA ESTRUTURAL
    # -----------------------------
    def infer_connections(self, node_id, threshold=0.5):
        """
        Sugere IECs relacionados por conexões de segundo grau.

        O retorno continua sendo uma lista de IECs, preservando o contrato
        usado pelo LifecycleManager e pelo Kernel atual.
        """
        node = self.graph.get_node(node_id)
        if not node:
            return []

        neighbors = self.graph.neighbors(node_id)
        suggestions = set()

        for neighbor in neighbors:
            for candidate in self.graph.neighbors(neighbor.id):
                if candidate.id != node_id:
                    suggestions.add(candidate.id)

        existing = {
            e["target"] if e["source"] == node_id else e["source"]
            for e in self.graph.edges_of(node_id)
        }

        return [
            self.graph.get_node(node_id_candidate)
            for node_id_candidate in suggestions
            if node_id_candidate not in existing
        ]

    # -----------------------------
    # 2. INFERÊNCIA SEMÂNTICA
    # -----------------------------
    def infer_semantic_connections(self, node_id, threshold=0.55):
        """
        Calcula similaridade semântica entre um IEC e os demais IECs.

        Retorna pares (source_id, target_id, score), compatíveis com a
        implementação histórica de inference.infer().
        """
        node = self.graph.get_node(node_id)
        if not node:
            return []

        connections = []

        for candidate_id, candidate in self.graph.nodes.items():
            if candidate_id == node_id:
                continue

            score = cosine_similarity(node.embedding, candidate.embedding)

            if score >= threshold:
                connections.append((node_id, candidate_id, score))

        connections.sort(key=lambda item: item[2], reverse=True)
        return connections

    # -----------------------------
    # 3. INFERÊNCIA POR EVIDÊNCIA
    # -----------------------------
    def infer_evidence_connections(self, node_id):
        """Sugere IECs que compartilham evidência com o nó informado.

        A sugestão é somente cognitiva: nenhuma aresta é criada aqui. O
        compartilhamento de evidência é um sinal para camadas superiores
        avaliarem, nunca uma prova automática de relação entre conceitos.
        """
        if not self.evidence_store or not self.graph.get_node(node_id):
            return []

        evidence_ids = {
            evidence["id"]
            for evidence in self.evidence_store.get_evidence_for_iec(node_id)
        }
        if not evidence_ids:
            return []

        candidates = {}
        for candidate_id in self.graph.nodes:
            if candidate_id == node_id:
                continue
            shared = {
                evidence["id"]
                for evidence in self.evidence_store.get_evidence_for_iec(candidate_id)
                if evidence["id"] in evidence_ids
            }
            if shared:
                candidates[candidate_id] = sorted(shared)

        return [
            {"node_id": candidate_id, "shared_evidence": evidence_ids}
            for candidate_id, evidence_ids in candidates.items()
        ]

    # -----------------------------
    # 3. INFERÊNCIA UNIFICADA
    # -----------------------------
    def infer(self, node_id, semantic_threshold=0.55):
        """
        Executa as duas estratégias de inferência sem apagar nenhuma delas.

        O resultado é deliberadamente explícito para que camadas superiores
        possam decidir como combinar evidência estrutural e semântica.
        """
        return {
            "node_id": node_id,
            "graph_connections": self.infer_connections(node_id),
            "semantic_connections": self.infer_semantic_connections(
                node_id,
                threshold=semantic_threshold,
            ),
            "evidence_connections": self.infer_evidence_connections(node_id),
        }

    # -----------------------------
    # 4. DETECÇÃO DE CONTRADIÇÃO
    # -----------------------------
    def detect_conflicts(self):
        """
        Detecta relações supports e contradicts simultâneas para o mesmo par.
        """
        conflicts = []

        for edge in self.graph.edges:
            if edge["type"] != "supports":
                continue

            source = edge["source"]
            target = edge["target"]

            for other in self.graph.edges:
                if (
                    other["source"] == source
                    and other["target"] == target
                    and other["type"] == "contradicts"
                ):
                    conflicts.append({
                        "source": source,
                        "target": target,
                        "issue": "support_vs_contradiction",
                    })

        return conflicts

    # -----------------------------
    # 5. PROPAGAÇÃO DE CONFIANÇA
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
            new_conf = (neighbor.confidence + influence) / 2
            neighbor.update_confidence(new_conf)
            propagated[neighbor.id] = new_conf

        return propagated

    # -----------------------------
    # 6. SUGESTÃO DE CONEXÕES
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

        return [
            self.graph.get_node(candidate_id)
            for candidate_id, count in candidates.items()
            if count >= min_common
        ]

    # -----------------------------
    # 7. RESUMO DO ESTADO COGNITIVO
    # -----------------------------
    def system_state(self):
        """
        Retorna uma visão geral do estado epistemológico do grafo.
        """
        return {
            "nodes": len(self.graph.nodes),
            "edges": len(self.graph.edges),
            "isolated": len(self.graph.isolated_nodes()),
            "low_confidence_edges": len(self.graph.low_confidence_edges()),
        }
