"""Camada de agentes do KALATRACE."""
from agents.agent_registry import AgentRegistry
from agents.base_agent import BaseAgent
from agents.reasoning_agent import ReasoningAgent
from agents.validation_agent import ValidationAgent

__all__ = ["AgentRegistry", "BaseAgent", "ReasoningAgent", "ValidationAgent"]
