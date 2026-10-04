"""Contratos para provedores de pesquisa científica."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Iterable


class ScientificProvider(ABC):
    """Contrato mínimo de um provedor usado pelo ScientificResearchEngine."""

    name = "scientific_provider"

    @abstractmethod
    def search(self, query: str) -> Iterable[Dict[str, Any]]:
        raise NotImplementedError

    def __call__(self, query: str) -> Iterable[Dict[str, Any]]:
        return self.search(query)


__all__ = ["ScientificProvider"]
