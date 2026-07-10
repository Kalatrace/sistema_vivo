"""
api/main.py — API do KALATRACE (opcional).

Roda com:
    uvicorn api.main:app --reload

Endpoints:
    POST /iec              -> cria um IEC e já roda inferência+governança+evolução
    GET  /graph             -> retorna o grafo atual
    GET  /health             -> métricas de saúde do sistema (4.0)
    GET  /curation/gaps      -> lacunas detectadas
    GET  /curation/duplicates -> duplicidades detectadas
    GET  /curation/conflicts -> conflitos detectados
"""

from fastapi import FastAPI
from pydantic import BaseModel

from core.engine import CoreEngine
from graph.graph import KnowledgeGraph
from inference.inference import infer
from governance.evaluator import Evaluator
from evolution.optimizer import Optimizer
from metacognition.self_model import SelfModel
from metacognition.observer import Observer
from metacognition.metrics import compute_system_health
from curation.curation import detect_duplicates, detect_gaps, detect_conflicts
from utils.embeddings import is_using_fallback

app = FastAPI(title="KALATRACE API")

engine = CoreEngine()
graph = KnowledgeGraph()
evaluator = Evaluator()
optimizer = Optimizer()
self_model = SelfModel()
observer = Observer(self_model)


class IECIn(BaseModel):
    id: str
    content: str
    node_type: str = "Conhecimento"


@app.post("/iec")
def create_iec(payload: IECIn):
    iec = engine.create_iec(payload.id, payload.content, node_type=payload.node_type)
    graph.add_node(iec)

    threshold = 0.3 if is_using_fallback() else 0.55
    connections = infer(graph, iec, threshold=threshold)
    for source, target, score in connections:
        graph.add_edge(source, target, "semantic_relation", score)

    evaluator.filter_edges(graph, min_score=0.15 if is_using_fallback() else 0.4)
    optimizer.reinforce_edges(graph)
    optimizer.prune_graph(graph, threshold=0.1)
    report = observer.monitor_cycle(graph, connections)

    return {
        "status": "created",
        "iec": iec.id,
        "connections": connections,
        "metacognition": report,
        "using_fallback_embedding": is_using_fallback(),
    }


@app.get("/graph")
def get_graph():
    return {
        "nodes": {nid: {"content": n.content, "node_type": n.node_type} for nid, n in graph.nodes.items()},
        "edges": graph.edges,
    }


@app.get("/health")
def get_health():
    return compute_system_health(graph, self_model)


@app.get("/curation/gaps")
def get_gaps():
    return detect_gaps(graph)


@app.get("/curation/duplicates")
def get_duplicates():
    return detect_duplicates(graph)


@app.get("/curation/conflicts")
def get_conflicts():
    return detect_conflicts(graph)
