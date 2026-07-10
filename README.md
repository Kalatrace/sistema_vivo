# KALATRACE — Backend Unificado (v1.0 → v4.0 + Curadoria)

Este projeto une, num único código coerente, as quatro versões que você
especificou (1.0 a 4.0), mais a parte do Blueprint Mestre (KLT-001) que
tinha regra concreta o suficiente para virar código.

## O que veio de cada versão

- **1.0** — `core/`, `graph/`, `inference/` (base), `memory/`
- **2.0** — `utils/embeddings.py`: troca a similaridade por palavras (Jaccard)
  por embeddings semânticos reais (`sentence-transformers`)
- **3.0** — `governance/` (avalia e filtra conexões) e `evolution/`
  (reforça/poda o grafo)
- **4.0** — `metacognition/` (o sistema observa o próprio comportamento)
- **Blueprint (Doc. 5 — Curadoria)** — `curation/`: Índice de Maturidade,
  Índice de Confiabilidade, estados do conhecimento, detectores de
  duplicidade/lacuna/conflito

## Como rodar

```bash
pip install -r requirements.txt
python run.py
```

Isso executa o ciclo completo: cria conhecimento → infere conexões →
avalia qualidade → evolui o grafo → o sistema observa a si mesmo →
classifica maturidade/confiabilidade → salva em `graph.json`.

Para a API:

```bash
uvicorn api.main:app --reload
```

Depois acesse `http://localhost:8000/docs` para testar os endpoints
interativamente.

## Sobre os embeddings (importante)

`utils/embeddings.py` tenta carregar o modelo real
(`all-MiniLM-L6-v2`, via `sentence-transformers`). **Isso exige internet**
na primeira execução (o modelo é baixado do Hugging Face). Se não houver
internet disponível, o sistema cai automaticamente para um modo offline
(hashing de palavras) só para não travar — mas isso NÃO é semântica real,
é um substituto de demonstração. Rode com internet pelo menos uma vez
para baixar o modelo de verdade; depois disso ele fica em cache local.

## O que ainda é placeholder, propositalmente

- `metacognition/self_model.py`: `error_rate` é uma métrica simulada,
  documentada como tal desde a sua versão 4.0. O gancho `log_correction()`
  já está pronto para quando houver feedback humano real (um curador
  confirmando ou rejeitando uma inferência) — aí a métrica passa a ser
  real, sem precisar mudar mais nada na estrutura.
- `curation/detect_conflicts`: é uma heurística de negação textual, não
  um julgamento científico. Para virar julgamento de verdade, o próximo
  passo é substituir essa função por uma chamada a um LLM lendo o
  conteúdo dos dois IECs.

## O que NÃO foi implementado (e por quê)

O Blueprint Mestre (Documentos 32 a 43) descreve um Vetor de Ponderação
Epistemológica e camadas de metacognição/autoevolução arquitetural onde a
própria fórmula matemática é deixada como espaço reservado no documento
original (`f` "pode ser linear ou logística — a definir"). Implementar
isso como equação fixa seria inventar uma regra que você não definiu.
Quando você tiver essa fórmula fechada (ou decidir que ela deve ser uma
chamada de IA em vez de equação), essa camada entra em
`governance/evaluator.py` sem quebrar nada do resto.
