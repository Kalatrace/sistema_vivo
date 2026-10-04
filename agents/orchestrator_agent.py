"""Agente de entrada para o Orchestrator do KALATRACE."""

from typing import Any, Dict

from agents.agent_registry import AgentRegistry
from agents.base_agent import BaseAgent
from core.orchestrator.orchestrator import Orchestrator


class OrchestratorAgent(BaseAgent):
    """Expõe o despacho do Orchestrator através do contrato de agentes."""

    name = "orchestrator"
    capabilities = ("agent_dispatch",)

    def __init__(
        self,
        registry: AgentRegistry,
        orchestrator: Orchestrator = None,
        agent_id: str = None,
    ):
        super().__init__(agent_id=agent_id)
        if registry is None:
            raise ValueError("OrchestratorAgent requer um AgentRegistry")
        self.registry = registry
        self.orchestrator = orchestrator or Orchestrator(registry)

    def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        payload = self.require_payload(payload)
        agent_id = payload.get("agent_id")
        task_payload = payload.get("payload", {})
        return {
            "agent": self.agent_id,
            "action": "dispatch",
            "result": self.orchestrator.dispatch(agent_id, task_payload),
        }
