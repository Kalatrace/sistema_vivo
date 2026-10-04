import unittest

from agents.base_agent import BaseAgent
from agents.agent_registry import AgentRegistry
from agents.orchestrator_agent import OrchestratorAgent
from core.orchestrator import Orchestrator


class EchoAgent(BaseAgent):
    name = "echo"

    def execute(self, payload):
        return {"received": payload}


class OrchestratorTests(unittest.TestCase):
    def setUp(self):
        self.registry = AgentRegistry()
        self.echo = self.registry.register(EchoAgent())
        self.orchestrator = Orchestrator(self.registry)

    def test_dispatch_routes_to_registered_agent(self):
        result = self.orchestrator.dispatch("echo", {"value": 7})
        self.assertEqual(result, {"received": {"value": 7}})

    def test_execute_accepts_structured_request(self):
        result = self.orchestrator.execute({
            "agent_id": "echo",
            "payload": {"task": "ping"},
        })
        self.assertEqual(result["received"]["task"], "ping")

    def test_unknown_agent_is_rejected(self):
        with self.assertRaises(KeyError):
            self.orchestrator.dispatch("missing", {})

    def test_orchestrator_agent_wraps_dispatch(self):
        agent = OrchestratorAgent(self.registry)
        result = agent.execute({
            "agent_id": "echo",
            "payload": {"value": 9},
        })
        self.assertEqual(result["agent"], "orchestrator")
        self.assertEqual(result["result"]["received"]["value"], 9)

    def test_invalid_payload_is_rejected(self):
        with self.assertRaises(TypeError):
            self.orchestrator.execute(["invalid"])


if __name__ == "__main__":
    unittest.main()
