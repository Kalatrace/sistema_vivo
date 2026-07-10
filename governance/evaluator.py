from utils.embeddings import cosine_similarity
from governance.rules import MIN_EDGE_WEIGHT


class Evaluator:
    """O 'juiz' do sistema (3.0): avalia a qualidade epistemológica de cada
    conexão do grafo e filtra as que não atingem o padrão mínimo."""

    def evaluate_edge(self, edge, graph):
        source = graph.get_node(edge["source"])
        target = graph.get_node(edge["target"])
        similarity = cosine_similarity(source.embedding, target.embedding)
        score = similarity * edge["weight"]
        return score

    def filter_edges(self, graph, min_score: float = MIN_EDGE_WEIGHT):
        valid_edges = []
        for edge in graph.edges:
            score = self.evaluate_edge(edge, graph)
            if score >= min_score:
                edge["quality_score"] = score
                valid_edges.append(edge)
        graph.edges = valid_edges
        return graph
