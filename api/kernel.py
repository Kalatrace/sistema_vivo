"""API canônica do Kernel epistemológico do KALATRACE.

Esta superfície não substitui ainda a API legada em api.main. Ela oferece
uma ponte explícita para o Kernel reconstruído, permitindo validar o contrato
antes da migração do entrypoint público.
"""

from fastapi import FastAPI
from pydantic import BaseModel, Field

from core.lifecycle_manager import LifecycleManager
from engines.curation import CurationEngine
from engines.reasoning.engine import ReasoningEngine
from graph.knowledge_graph import KnowledgeGraph
from knowledge.iec import IEC
from memory.evidence_store import EvidenceStore
from validation.validation_engine import ValidationEngine

graph = KnowledgeGraph()
evidence_store = EvidenceStore()
validator = ValidationEngine(graph, evidence_store)
reasoner = ReasoningEngine(graph, evidence_store=evidence_store)
curation = CurationEngine(graph)
lifecycle = LifecycleManager(graph, evidence_store, validator, reasoner)

app = FastAPI(title="KALATRACE Kernel API")

class IECIn(BaseModel):
    id: str
    content: str
    domain: str | None = None
    node_type: str = "Conhecimento"
    embedding: list[float] | None = None
    metadata: dict = Field(default_factory=dict)

class EvidenceIn(BaseModel):
    evidence_id: str
    content: dict
    source_type: str = "unknown"
    reliability: float = 0.5

class RelationIn(BaseModel):
    source: str
    target: str
    evidence_ids: list[str]
    relation_type: str = "supports"
    weight: float = 1.0
    threshold: float = 0.75

class ReliabilityIn(BaseModel):
    factors: dict[str, float]
    weights: dict[str, float] | None = None

class KnowledgeStateIn(BaseModel):
    maturity_score: float
    reliability_score: float
    has_active_conflict: bool = False
    superseded_by: str | None = None

@app.get("/health")
def health():
    return {"status": "ok", "kernel": "canonical"}

@app.post("/iec")
def create_iec(payload: IECIn):
    iec = IEC(id=payload.id, content=payload.content, domain=payload.domain,
              node_type=payload.node_type, embedding=payload.embedding,
              metadata=payload.metadata)
    lifecycle.create_iec(iec)
    return {"status": "created", "iec": iec.id}

@app.post("/iec/{iec_id}/evidence")
def attach_evidence(iec_id: str, payload: EvidenceIn):
    lifecycle.attach_evidence(iec_id=iec_id, evidence_id=payload.evidence_id,
                               content=payload.content, reliability=payload.reliability, source_type=payload.source_type)
    return {"status": "attached", "iec": iec_id, "evidence": payload.evidence_id}

@app.post("/relations/promote")
def promote_relation(payload: RelationIn):
    return lifecycle.promote_relation(source_id=payload.source, target_id=payload.target,
                                      evidence_ids=payload.evidence_ids,
                                      relation_type=payload.relation_type,
                                      weight=payload.weight, threshold=payload.threshold)

@app.get("/iec/{iec_id}/reason")
def reason(iec_id: str):
    return {"iec": iec_id, "reasoning": reasoner.infer(iec_id)}

@app.get("/iec/{iec_id}/validation")
def validate(iec_id: str):
    return validator.validate_iec(iec_id)

@app.get("/curation/gaps")
def curation_gaps():
    return {"gaps": curation.detect_gaps()}

@app.get("/curation/duplicates")
def curation_duplicates(threshold: float = 0.92):
    if threshold < 0.0 or threshold > 1.0:
        raise ValueError("O threshold deve estar entre 0 e 1")
    return {"duplicates": curation.detect_duplicates(threshold=threshold), "threshold": threshold}

@app.post("/curation/reliability")
def curation_reliability(payload: ReliabilityIn):
    return {"score": curation.reliability_score(payload.factors, payload.weights)}

@app.post("/curation/knowledge-state")
def curation_knowledge_state(payload: KnowledgeStateIn):
    state = curation.classify_knowledge_state(
        payload.maturity_score,
        payload.reliability_score,
        has_active_conflict=payload.has_active_conflict,
        superseded_by=payload.superseded_by,
    )
    return {"state": state}

@app.get("/graph")
def get_graph():
    return {"nodes": {node_id: {"content": node.content, "domain": node.domain,
             "node_type": node.node_type, "confidence": node.confidence,
             "metadata": node.metadata} for node_id, node in graph.nodes.items()},
            "edges": graph.edges}

@app.get("/status")
def status():
    return lifecycle.status()

__all__ = ["app", "graph", "evidence_store", "validator", "reasoner", "curation", "lifecycle"]