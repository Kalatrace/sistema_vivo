import unittest

from engines.base.base_engine import BaseEngine, CoreEngine


class ExampleEngine(BaseEngine):
    name = "example"

    def execute(self, payload):
        return {"received": payload}


class BaseEngineTests(unittest.TestCase):
    def test_base_engine_delegates_run_to_execute(self):
        engine = ExampleEngine()
        payload = {"value": 3}
        self.assertEqual(engine.run(payload), {"received": payload})
        self.assertEqual(engine.engine_id, "example")

    def test_core_engine_keeps_iec_factory_compatibility(self):
        engine = CoreEngine()
        iec = engine.create_iec("iec-1", "Conhecimento", domain="science")
        self.assertEqual(iec.id, "iec-1")
        self.assertEqual(iec.content, "Conhecimento")
        self.assertEqual(iec.domain, "science")

    def test_core_engine_has_minimal_runtime_contract(self):
        result = CoreEngine().execute({})
        self.assertEqual(result["engine"], "core")
        self.assertEqual(result["status"], "ready")


if __name__ == "__main__":
    unittest.main()
