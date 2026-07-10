class KnowledgeGraph:
    def __init__(self):
        self.nodes = {}
        self.edges = []

    # -----------------------
    # NODES
    # -----------------------
    def add_node(self, iec):
        """
        Adiciona um nó (IEC - unidade de conhecimento)
        """
        self.nodes[iec.id] = iec

    def get_node(self, node_id):
        return self.nodes.get(node_id)

    # -----------------------
    # EDGES
    # -----------------------
    def add_edge(
        self,
        source,
        target,
        relation_type="related",
        weight=1.0,
        confidence=0.5,
        evidence=None,
    ):
        """
        Adiciona uma relação epistemológica entre dois nós.
        Agora inclui:
        - confidence (qualidade da relação)
        - evidence (justificativa da ligação)
        """

        if evidence is None:
            evidence = []

        self.edges.append({
            "source": source,
            "target": target,
            "type": relation_type,
            "weight": float(weight),
            "confidence": float(confidence),
            "evidence": evidence,
        })

    # -----------------------
    # QUERY
    # -----------------------
    def edges_of(self, node_id):
        """
        Todas as arestas conectadas a um nó
        """
        return [
            e for e in self.edges
            if e["source"] == node_id or e["target"] == node_id
        ]

    def neighbors(self, node_id):
        """
        Retorna nós vizinhos diretos (importante para navegação cognitiva)
        """
        result = set()

        for e in self.edges:
            if e["source"] == node_id:
                result.add(e["target"])
            elif e["target"] == node_id:
                result.add(e["source"])

        return [self.nodes[n] for n in result if n in self.nodes]

    # -----------------------
    # LACUNAS E QUALIDADE
    # -----------------------
    def isolated_nodes(self):
        """
        Nós sem conexão (lacunas epistemológicas)
        """
        connected = set()

        for e in self.edges:
            connected.add(e["source"])
            connected.add(e["target"])

        return [
            self.nodes[nid]
            for nid in self.nodes
            if nid not in connected
        ]

    def low_confidence_edges(self, threshold=0.3):
        """
        Relações fracas → candidatos a revisão
        """
        return [
            e for e in self.edges
            if e.get("confidence", 1.0) < threshold
        ]

    # -----------------------
    # MANIPULAÇÃO BÁSICA
    # -----------------------
    def remove_edge(self, source, target):
        """
        Remove conexão específica
        """
        self.edges = [
            e for e in self.edges
            if not (e["source"] == source and e["target"] == target)
        ]

    def remove_node(self, node_id):
        """
        Remove nó e todas suas conexões
        """
        if node_id in self.nodes:
            del self.nodes[node_id]

        self.edges = [
            e for e in self.edges
            if e["source"] != node_id and e["target"] != node_id
        ]

    # -----------------------
    # STATUS
    # -----------------------
    def stats(self):
        return {
            "nodes": len(self.nodes),
            "edges": len(self.edges),
            "isolated_nodes": len(self.isolated_nodes()),
        }

    def __repr__(self):
        s = self.stats()
        return (
            f"KnowledgeGraph("
            f"nodes={s['nodes']}, "
            f"edges={s['edges']}, "
            f"isolated={s['isolated_nodes']}"
            f")"
        )