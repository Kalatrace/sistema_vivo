"""Agente que delega validações ao ValidationEngine existente."""
from typing import Any, Dict

from agents.base_agent import BaseAgent
from validation.validation_engine import ValidationEngine


class ValidationAgent(BaseAgent):
    name = "validation"
    capabilities = ("validate_iec", "validate_graph", "quality_report")

    def __init__(self, validation_engine: ValidationEngine, agent_id: str = None):
        super().__init__(agent_id=agent_id)
        if validation_engine is None:
            raise ValueError("ValidationAgent requer um ValidationEngine")
        self.validation_engine = validation_engine

    def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        payload = self.require_payload(payload)
        action = payload.get("action", "validate")
        iec_id = payload.get("iec_id")

        if action == "validate":
            result = (self.validation_engine.validate_iec(iec_id)
                      if iec_id else self.validation_engine.validate_all())
            return {"agent": self.agent_id, "action": action, "result": result}
        if action == "report":
            result = self.validation_engine.report()
            return {"agent": self.agent_id, "action": action, "result": result}
        if action == "quality_score":
            result = self.validation_engine.system_quality_score()
            return {"agent": self.agent_id, "action": action, "result": result}
        if action == "weak_knowledge":
            result = self.validation_engine.weak_knowledge(
                threshold=payload.get("threshold", 0.5))
            return {"agent": self.agent_id, "action": action, "result": result}
        raise ValueError(f"Ação de validação não suportada: {action}")
