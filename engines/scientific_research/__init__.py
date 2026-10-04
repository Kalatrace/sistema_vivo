"""Componentes canônicos de pesquisa científica do KALATRACE."""

from engines.scientific_research.engine import ScientificResearchEngine
from engines.scientific_research.evidence import ScientificEvidenceBridge
from engines.scientific_research.provider import ScientificProvider
from engines.scientific_research.search_pipeline import ScientificSearchPipeline

__all__ = [
    "ScientificResearchEngine",
    "ScientificEvidenceBridge",
    "ScientificProvider",
    "ScientificSearchPipeline",
]
