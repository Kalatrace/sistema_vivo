"""Contrato comum para agentes do KALATRACE.

Agentes coordenam capacidades existentes; não substituem o Kernel cognitivo.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseAgent(ABC):
    """Interface mínima de execução de um agente."""

    name = "base"
    capabilities = ()

    def __init__(self, agent_id: str = None):
        self.agent_id = agent_id or self.name

    @abstractmethod
    def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Executa uma tarefa e devolve um resultado estruturado."""
        raise NotImplementedError

    def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Alias semântico para execução, útil aos futuros orquestradores."""
        return self.execute(payload)

    @staticmethod
    def require_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
        if not isinstance(payload, dict):
            raise TypeError("O payload do agente deve ser um dicionário")
        return payload
