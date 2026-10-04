"""Agente que expõe o ScientificResearchEngine através do contrato de agentes."""
from typing import Any, Dict

from agents.base_agent import BaseAgent
from engines.scientific_research import ScientificResearchEngine


class ResearchAgent(BaseAgent):
    name = "research"
    capabilities = ("scientific_search", "provider_search")

    def __init__(self, research_engine: ScientificResearchEngine, agent_id: str = None):
        super().__init__(agent_id=agent_id)
        if research_engine is None:
            raise ValueError("ResearchAgent requer um ScientificResearchEngine")
        self.research_engine = research_engine

    def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        payload = self.require_payload(payload)
        action = payload.get("action", "search")

        if action in ("search", "scientific_search"):
            query = payload.get("query")
            provider = payload.get("provider")
            result = self.research_engine.search(query, provider=provider)
            return {
                "agent": self.agent_id,
                "action": "search",
                "result": result,
                "count": len(result),
            }

        if action == "execute":
            result = self.research_engine.execute(payload)
            return {"agent": self.agent_id, "action": action, "result": result}

        raise ValueError(f"Ação de pesquisa não suportada: {action}")
