import unittest
from unittest.mock import Mock

from agents.agent_registry import AgentRegistry
from agents.base_agent import BaseAgent
from agents.reasoning_agent import ReasoningAgent
from agents.validation_agent import ValidationAgent


class AgentFoundationTests(unittest.TestCase):
    def test_base_agent_run_delegates_to_execute(self):
        class EchoAgent(BaseAgent):
            name = "echo"
            def execute(self, payload):
                return payload

        agent = EchoAgent()
        payload = {"value": 7}
        self.assertIs(agent.run(payload), payload)

    def test_registry_registers_and_retrieves_agent(self):
        class EchoAgent(BaseAgent):
            name = "echo"
            def execute(self, payload):
                return payload

        registry = AgentRegistry()
        agent = EchoAgent()
        registry.register(agent)
        self.assertIs(registry.get("echo"), agent)
        self.assertEqual(registry.names(), ["echo"])
        self.assertEqual(len(registry), 1)

    def test_registry_rejects_duplicate_ids(self):
        class EchoAgent(BaseAgent):
            name = "echo"
            def execute(self, payload):
                return payload

        registry = AgentRegistry()
        registry.register(EchoAgent())
        with self.assertRaises(ValueError):
            registry.register(EchoAgent())

    def test_reasoning_agent_delegates_inference(self):
        engine = Mock()
        engine.infer.return_value = {"node_id": "n1", "graph_connections": []}
        agent = ReasoningAgent(engine)
        result = agent.execute({"node_id": "n1"})
        engine.infer.assert_called_once_with("n1")
        self.assertEqual(result["result"]["node_id"], "n1")

    def test_validation_agent_delegates_single_iec_validation(self):
        engine = Mock()
        engine.validate_iec.return_value = {"valid": True}
        agent = ValidationAgent(engine)
        result = agent.execute({"action": "validate", "iec_id": "iec-1"})
        engine.validate_iec.assert_called_once_with("iec-1")
        self.assertEqual(result["result"], {"valid": True})

    def test_agents_reject_invalid_payload(self):
        engine = Mock()
        with self.assertRaises(TypeError):
            ReasoningAgent(engine).execute(["not", "a", "dict"])


if __name__ == "__main__":
    unittest.main()
