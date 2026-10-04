"""Agente que expõe o ReasoningEngine através do contrato de agentes."""
from typing import Any, Dict

from agents.base_agent import BaseAgent
from engines.reasoning.engine import ReasoningEngine


class ReasoningAgent(BaseAgent):
    name = "reasoning"
    capabilities = ("graph_reasoning", "semantic_reasoning", "evidence_reasoning", "conflict_detection")

    def __init__(self, reasoning_engine: ReasoningEngine, agent_id: str = None):
        super().__init__(agent_id=agent_id)
        if reasoning_engine is None:
            raise ValueError("ReasoningAgent requer um ReasoningEngine")
        self.reasoning_engine = reasoning_engine

    def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        payload = self.require_payload(payload)
        action = payload.get("action", "infer")
        node_id = payload.get("node_id")

        if action in ("infer", "infer_connections"):
            if not node_id:
                raise ValueError("'node_id' é obrigatório para inferência")
            result = self.reasoning_engine.infer(node_id)
            return {"agent": self.agent_id, "action": "infer", "result": result}

        if action == "detect_conflicts":
            result = self.reasoning_engine.detect_conflicts()
            return {"agent": self.agent_id, "action": action, "result": result}

        if action == "system_state":
            result = self.reasoning_engine.system_state()
            return {"agent": self.agent_id, "action": action, "result": result}

        raise ValueError(f"Ação de raciocínio não suportada: {action}")
