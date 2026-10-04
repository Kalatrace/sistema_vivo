"""Orquestrador mínimo do KALATRACE.

O Orchestrator apenas seleciona e despacha para agentes registrados.
Ele não contém lógica cognitiva, não substitui engines e não agenda tarefas.
"""
from typing import Any, Dict

from agents.agent_registry import AgentRegistry


class Orchestrator:
    """Despacha uma tarefa para um agente registrado."""

    def __init__(self, registry: AgentRegistry):
        if registry is None:
            raise ValueError("Orchestrator requer um AgentRegistry")
        self.registry = registry

    def dispatch(self, agent_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        if not agent_id:
            raise ValueError("'agent_id' é obrigatório")
        if not isinstance(payload, dict):
            raise TypeError("O payload do orquestrador deve ser um dicionário")

        agent = self.registry.get(agent_id)
        return agent.run(payload)

    def execute(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Executa uma requisição estruturada: {agent_id, payload}."""
        if not isinstance(request, dict):
            raise TypeError("A requisição do orquestrador deve ser um dicionário")

        agent_id = request.get("agent_id")
        payload = request.get("payload", {})
        return self.dispatch(agent_id, payload)
