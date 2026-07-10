"""
run.py — KALATRACE unificado (1.0 -> 4.0 + curadoria)

Ciclo completo:
  1. Criar conhecimento (IECs)                    [1.0]
  2. Inferência semântica real (embeddings)       [2.0]
  3. Governança: avaliar e filtrar conexões       [3.0]
  4. Evolução: reforçar/podar o grafo             [3.0]
  5. Metacognição: o sistema observa a si mesmo   [4.0]
  6. Curadoria: maturidade, confiabilidade,
     duplicidades, lacunas, conflitos             [Blueprint Doc. 5]
  7. Memória: persistir tudo em JSON
"""

from utils.embeddings import is_using_fallback
from core.engine import CoreEngine
from graph.graph import KnowledgeGraph
from inference.inference import infer
from governance.evaluator import Evaluator
from evolution.optimizer import Optimizer
from metacognition.self_model import SelfModel
from metacognition.observer import Observer
from metacognition.metrics import compute_system_health
from curation.curation import (
    maturity_label, reliability_score, classify_knowledge_state,
    detect_duplicates, detect_gaps, detect_conflicts,
)
from memory.memory import save_graph


def main():
    if is_using_fallback():
        print("⚠️  Rodando com embedding OFFLINE (fallback por hashing).")
        print("   Sem internet para baixar o modelo real (sentence-transformers).")
        print("   Instale as dependências e rode com internet para semântica real.\n")

    engine = CoreEngine()
    graph = KnowledgeGraph()

    # 1. Conhecimento base (exemplo: linha de pesquisa Bakuchiol/Resveratrol)
    iec1 = engine.create_iec("1", "bakuchiol reduz marcadores de inflamação cutânea", node_type="Evidência")
    iec2 = engine.create_iec("2", "resveratrol ativa a expressão de SIRT1 em fibroblastos", node_type="Evidência")
    iec3 = engine.create_iec("3", "bakuchiol estimula a produção de colágeno tipo I", node_type="Evidência")
    iec4 = engine.create_iec("4", "protocolo de ensaio de toxicidade aguda em modelo animal", node_type="Experimento")

    for iec in (iec1, iec2, iec3, iec4):
        graph.add_node(iec)

    # 2. Novo conhecimento chega ao sistema -> inferência semântica
    new_iec = engine.create_iec(
        "5", "bakuchiol tem atividade antioxidante e reduz inflamação na pele",
        node_type="Hipótese",
    )
    graph.add_node(new_iec)

    connections = infer(graph, new_iec, threshold=0.3 if is_using_fallback() else 0.55)
    for source, target, score in connections:
        graph.add_edge(source, target, "semantic_relation", score)

    # 3. Governança — avalia e filtra conexões fracas
    evaluator = Evaluator()
    graph = evaluator.filter_edges(graph, min_score=0.15 if is_using_fallback() else 0.4)

    # 4. Evolução — reforça conexões boas, poda o resto
    optimizer = Optimizer()
    graph = optimizer.reinforce_edges(graph)
    graph = optimizer.prune_graph(graph, threshold=0.1)

    # 5. Metacognição — o sistema observa o próprio ciclo
    self_model = SelfModel()
    observer = Observer(self_model)
    metacog_report = observer.monitor_cycle(graph, connections)
    health = compute_system_health(graph, self_model)

    # 6. Curadoria — classificação epistemológica (exemplo de uso manual;
    #    numa versão real esses fatores viriam de dados reais do estudo)
    example_factors = {
        "methodological_quality": 0.8,
        "sample_size": 0.6,
        "bias_risk_inverted": 0.7,
        "reproducibility": 0.75,
        "statistical_consistency": 0.8,
        "recency": 0.9,
    }
    rel_score = reliability_score(example_factors)
    maturity_score = 68  # exemplo — na prática, calculado a partir do nº/qualidade de estudos
    state = classify_knowledge_state(maturity_score, rel_score)

    duplicates = detect_duplicates(graph, threshold=0.85 if is_using_fallback() else 0.92)
    gaps = detect_gaps(graph)
    conflicts = detect_conflicts(graph, similarity_threshold=0.3 if is_using_fallback() else 0.6)

    # 7. Memória
    save_graph(graph, filename="graph.json")

    # ---- Relatório do ciclo ----
    print("=== GRAFO ===")
    print(graph)
    print("\n=== CONEXÕES INFERIDAS ===")
    for s, t, score in connections:
        print(f"  {s} -> {t}  (score={score:.3f})")
    print("\n=== METACOGNIÇÃO ===")
    print(" ", metacog_report)
    print("\n=== SAÚDE DO SISTEMA ===")
    print(" ", health)
    print("\n=== CURADORIA (exemplo) ===")
    print(f"  Maturidade: {maturity_score}% -> {maturity_label(maturity_score)}")
    print(f"  Confiabilidade: {rel_score}%")
    print(f"  Estado do conhecimento: {state}")
    print(f"  Duplicidades detectadas: {duplicates}")
    print(f"  Lacunas detectadas: {gaps}")
    print(f"  Conflitos detectados: {conflicts}")


if __name__ == "__main__":
    main()
