"""Contrato base para engines cognitivos do KALATRACE."""

from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseEngine(ABC):
    """Interface mínima comum aos engines cognitivos."""

    name = "base"

    def __init__(self, engine_id: str | None = None):
        self.engine_id = engine_id or self.name

    @abstractmethod
    def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Executa uma operação do engine."""
        raise NotImplementedError

    def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Alias estável para execução."""
        return self.execute(payload)


class CoreEngine(BaseEngine):
    """Fábrica compatível de IECs para a camada de engenharia."""

    name = "core"

    def create_iec(
        self,
        id,
        content,
        node_type="Conhecimento",
        metadata=None,
        domain=None,
    ):
        from knowledge.iec import IEC

        return IEC(
            id=id,
            content=content,
            domain=domain,
            node_type=node_type,
            metadata=metadata,
        )

    def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        if not isinstance(payload, dict):
            raise TypeError("O payload do engine deve ser um dicionário")
        return {"engine": self.engine_id, "action": "noop", "status": "ready"}


__all__ = ["BaseEngine", "CoreEngine"]
