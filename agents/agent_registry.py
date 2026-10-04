"""Registro explícito de agentes disponíveis no sistema."""
from typing import Dict, List

from agents.base_agent import BaseAgent


class AgentRegistry:
    def __init__(self):
        self._agents: Dict[str, BaseAgent] = {}

    def register(self, agent: BaseAgent) -> BaseAgent:
        if not isinstance(agent, BaseAgent):
            raise TypeError("Somente instâncias de BaseAgent podem ser registradas")
        key = agent.agent_id
        if key in self._agents:
            raise ValueError(f"Já existe um agente registrado com o id '{key}'")
        self._agents[key] = agent
        return agent

    def get(self, agent_id: str) -> BaseAgent:
        try:
            return self._agents[agent_id]
        except KeyError as exc:
            raise KeyError(f"Agente não registrado: {agent_id}") from exc

    def unregister(self, agent_id: str) -> BaseAgent:
        try:
            return self._agents.pop(agent_id)
        except KeyError as exc:
            raise KeyError(f"Agente não registrado: {agent_id}") from exc

    def list_agents(self) -> List[BaseAgent]:
        return list(self._agents.values())

    def names(self) -> List[str]:
        return list(self._agents.keys())

    def __len__(self) -> int:
        return len(self._agents)
