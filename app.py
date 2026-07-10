from core.knowledge_graph import KnowledgeGraph
from engine.reasoning_engine import ReasoningEngine
from storage.evidence_store import EvidenceStore
from validation.validation_engine import ValidationEngine
from engine.curiosity_engine import CuriosityEngine

# -----------------------------
# SISTEMA
# -----------------------------
graph = KnowledgeGraph()
reasoner = ReasoningEngine(graph)
evidence_store = EvidenceStore()
validator = ValidationEngine(graph, evidence_store)
curiosity = CuriosityEngine(graph, evidence_store, validator)

# -----------------------------
# IECs
# -----------------------------
class IEC:
    def __init__(self, id, content):
        self.id = id
        self.content = content

iec1 = IEC("IEC-001", "Bakuchiol estimula síntese de colágeno")
iec2 = IEC("IEC-002", "Colágeno melhora regeneração da pele")
iec3 = IEC("IEC-003", "Inflamação reduz síntese de colágeno")  # mais fraco

graph.add_node(iec1)
graph.add_node(iec2)
graph.add_node(iec3)

# -----------------------------
# RELAÇÕES
# -----------------------------
graph.add_edge("IEC-001", "IEC-002", "causa_indireta", 0.8)
graph.add_edge("IEC-003", "IEC-001", "inibe", 0.6)

# -----------------------------
# EVIDÊNCIA
# -----------------------------
evidence_store.add_evidence(
    "IEC-001",
    "Journal of Dermatology 2023",
    "clinical_study",
    0.85
)

evidence_store.add_evidence(
    "IEC-002",
    "Skin Biology Review 2022",
    "review",
    0.75
)

# IEC-003 propositalmente sem evidência forte

# -----------------------------
# EXECUÇÃO
# -----------------------------
print("KALATRACE iniciado 🚀")

print("\n--- GRAFO ---")
print("Nós:", graph.nodes)
print("Edges:", graph.edges)

print("\n--- RACIOCÍNIO ---")
print(reasoner.explain_connection("IEC-001", "IEC-002"))

print("\n--- VALIDAÇÃO ---")
print(validator.validate_graph())

print("\n--- CURIOSIDADE (PRIORIDADES DE EXPLORAÇÃO) ---")
for item in curiosity.suggest_next_exploration():
    print(item)