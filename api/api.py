from fastapi import FastAPI
from pydantic import BaseModel

# Core imports
from kalatrace.core.iec import IEC
from kalatrace.core.knowledge_graph import KnowledgeGraph
from kalatrace.core.reasoning_engine import ReasoningEngine
from kalatrace.core.evidence_store import EvidenceStore
from kalatrace.core.validation_engine import ValidationEngine
from kalatrace.core.lifecycle_manager import LifecycleManager

# -----------------------------
# INIT SISTEMA
# -----------------------------
graph = KnowledgeGraph()
evidence_store = EvidenceStore()

reasoner = ReasoningEngine(graph)
validator = ValidationEngine(graph, evidence_store)

lifecycle = LifecycleManager(
    graph=graph,
    evidence_store=evidence_store,
    validator=validator,
    reasoner=reasoner
)

app = FastAPI(title="KALATRACE API")

# -----------------------------
# MODELS (INPUTS)
# -----------------------------
class IECInput(BaseModel):
    id: str
    content: str
    domain: str = None


class EdgeInput(BaseModel):
    source: str
    target: str
    relation_type: str = "related"
    weight: float = 1.0


class EvidenceInput(BaseModel):
    iec_id: str
    evidence_id: str
    content: str
    reliability: float = 0.5


# -----------------------------
# ENDPOINTS
# -----------------------------

@app.post("/iec/create")
def create_iec(data: IECInput):
    iec = IEC(data.id, data.content, data.domain)
    lifecycle.create_iec(iec)
    return {"status": "created", "iec_id": data.id}


@app.post("/edge/create")
def create_edge(data: EdgeInput):
    lifecycle.connect(
        source_id=data.source,
        target_id=data.target,
        relation_type=data.relation_type,
        weight=data.weight
    )
    return {"status": "edge_created"}


@app.post("/evidence/add")
def add_evidence(data: EvidenceInput):
    lifecycle.attach_evidence(
        iec_id=data.iec_id,
        evidence_id=data.evidence_id,
        content=data.content,
        reliability=data.reliability
    )
    return {"status": "evidence_added"}


@app.get("/validate/all")
def validate_all():
    result = lifecycle.validate()
    return {"validation": result}


@app.get("/reason/{iec_id}")
def reason(iec_id: str):
    result = lifecycle.reason(iec_id)
    return {"suggestions": [n.id for n in result] if result else []}


@app.get("/status")
def system_status():
    return lifecycle.status()


@app.get("/cycle/run")
def run_cycle():
    return lifecycle.run_cycle()