"""Pipeline canônico para orquestrar buscas científicas multi-provider."""

from typing import Any, Dict, Iterable, List

from engines.scientific_research.parser import normalize_results
from engines.scientific_research.provider import ScientificProvider


class ScientificSearchPipeline:
    """Executa buscas em provedores já registrados sem acoplar transporte."""

    def __init__(self, providers: Iterable[ScientificProvider] | None = None):
        self.providers: Dict[str, ScientificProvider] = {}
        for provider in providers or ():
            self.register_provider(provider)

    def register_provider(self, provider: ScientificProvider) -> None:
        if not isinstance(provider, ScientificProvider):
            raise TypeError("O provedor deve implementar ScientificProvider")
        if not provider.name:
            raise ValueError("O provedor deve possuir um nome")
        if provider.name in self.providers:
            raise ValueError(f"Provedor já registrado: {provider.name}")
        self.providers[provider.name] = provider

    def search(self, query: str, providers: Iterable[str] | None = None) -> List[Dict[str, Any]]:
        if not isinstance(query, str) or not query.strip():
            raise ValueError("A consulta científica não pode ser vazia")

        selected = list(providers) if providers is not None else list(self.providers)
        for name in selected:
            if name not in self.providers:
                raise KeyError(f"Provedor científico não registrado: {name}")

        results: List[Dict[str, Any]] = []
        for name in selected:
            raw = self.providers[name].search(query)
            results.extend(normalize_results(raw, provider=name, query=query))
        return results

    def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        if not isinstance(payload, dict):
            raise TypeError("O payload do pipeline deve ser um dicionário")
        query = payload.get("query")
        providers = payload.get("providers")
        results = self.search(query, providers=providers)
        return {
            "pipeline": "scientific_search",
            "query": query,
            "providers": list(providers) if providers is not None else list(self.providers),
            "results": results,
            "count": len(results),
        }


__all__ = ["ScientificSearchPipeline"]
