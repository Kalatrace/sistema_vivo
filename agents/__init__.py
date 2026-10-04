"""Agentes canônicos do KALATRACE."""

from agents.base_agent import BaseAgent
from agents.agent_registry import AgentRegistry
from agents.reasoning_agent import ReasoningAgent
from agents.validation_agent import ValidationAgent
from agents.orchestrator_agent import OrchestratorAgent
from agents.research_agent import ResearchAgent

__all__ = [
    "BaseAgent",
    "AgentRegistry",
    "ReasoningAgent",
    "ValidationAgent",
    "OrchestratorAgent",
    "ResearchAgent",
]
