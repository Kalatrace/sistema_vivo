"""Engine canônico de pesquisa científica do KALATRACE."""

from typing import Any, Callable, Dict, Iterable, List

from engines.base.base_engine import BaseEngine


class ScientificResearchEngine(BaseEngine):
    """Coordena pesquisa científica sem acoplar o Kernel a um provedor."""

    name = "scientific_research"

    def __init__(
        self,
        providers: Dict[str, Callable[[str], Iterable[Dict[str, Any]]]] | None = None,
        engine_id: str | None = None,
    ):
        super().__init__(engine_id=engine_id)
        self.providers = dict(providers or {})

    def register_provider(self, name: str, provider: Callable[[str], Iterable[Dict[str, Any]]]) -> None:
        if not name:
            raise ValueError("O nome do provedor é obrigatório")
        if not callable(provider):
            raise TypeError("O provedor deve ser chamável")
        self.providers[name] = provider

    def search(self, query: str, provider: str | None = None) -> List[Dict[str, Any]]:
        if not isinstance(query, str) or not query.strip():
            raise ValueError("A consulta científica não pode ser vazia")
        selected = [provider] if provider else list(self.providers)
        if provider and provider not in self.providers:
            raise KeyError(f"Provedor científico não registrado: {provider}")
        results: List[Dict[str, Any]] = []
        for name in selected:
            raw = self.providers[name](query)
            for item in raw or []:
                if not isinstance(item, dict):
                    raise TypeError("Provedores devem retornar dicionários")
                normalized = dict(item)
                normalized.setdefault("provider", name)
                normalized.setdefault("query", query)
                results.append(normalized)
        return results

    def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        if not isinstance(payload, dict):
            raise TypeError("O payload do engine deve ser um dicionário")
        query = payload.get("query")
        provider = payload.get("provider")
        results = self.search(query, provider=provider)
        return {"engine": self.engine_id, "query": query, "provider": provider, "results": results, "count": len(results)}


__all__ = ["ScientificResearchEngine"]
