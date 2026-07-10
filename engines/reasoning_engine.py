class ReasoningEngine:
    def __init__(self, graph):
        """
        graph: KnowledgeGraph instance
        """
        self.graph = graph

    # -----------------------------
    # 1. Buscar vizinhos diretos
    # -----------------------------
    def get_neighbors(self, node_id):
        neighbors = []

        for edge in self.graph.edges:
            if edge["source"] == node_id:
                neighbors.append(edge["target"])
            elif edge["target"] == node_id:
                neighbors.append(edge["source"])

        return list(set(neighbors))

    # -----------------------------
    # 2. Buscar caminhos (DFS simples)
    # -----------------------------
    def find_paths(self, start_id, end_id, path=None):
        if path is None:
            path = []

        path = path + [start_id]

        if start_id == end_id:
            return [path]

        if start_id not in self.graph.nodes:
            return []

        paths = []

        for neighbor in self.get_neighbors(start_id):
            if neighbor not in path:  # evita loop
                new_paths = self.find_paths(neighbor, end_id, path)
                for p in new_paths:
                    paths.append(p)

        return paths

    # -----------------------------
    # 3. Verificar conexão entre nós
    # -----------------------------
    def is_connected(self, start_id, end_id):
        paths = self.find_paths(start_id, end_id)
        return len(paths) > 0

    # -----------------------------
    # 4. Caminho mais curto (simples)
    # -----------------------------
    def shortest_path(self, start_id, end_id):
        paths = self.find_paths(start_id, end_id)

        if not paths:
            return None

        return min(paths, key=len)

    # -----------------------------
    # 5. Debug do raciocínio
    # -----------------------------
    def explain_connection(self, start_id, end_id):
        paths = self.find_paths(start_id, end_id)

        if not paths:
            return {
                "connected": False,
                "reason": "No path found"
            }

        return {
            "connected": True,
            "paths": paths,
            "shortest": min(paths, key=len)
        }