"""Adapter do Semantic Scholar sem acoplamento ao transporte HTTP."""
from typing import Any, Callable, Dict, Iterable
from engines.scientific_research.provider import ScientificProvider

class SemanticScholarClient(ScientificProvider):
    name = "semantic_scholar"
    def __init__(self, search_fn: Callable[[str], Iterable[Dict[str, Any]]] | None = None):
        self.search_fn = search_fn
    def search(self, query: str) -> Iterable[Dict[str, Any]]:
        if not self.search_fn:
            raise RuntimeError("SemanticScholarClient requer um transporte de pesquisa configurado")
        return self.search_fn(query)

__all__ = ["SemanticScholarClient"]
