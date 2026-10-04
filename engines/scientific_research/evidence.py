"""Ponte entre resultados de pesquisa científica e evidências do Kernel.

O módulo preserva o resultado normalizado como conteúdo da evidência e usa o
EvidenceStore canônico como única porta de persistência epistemológica.
"""

import hashlib
import json
from typing import Any, Dict, Iterable, List


class ScientificEvidenceBridge:
    """Converte resultados científicos em evidências vinculadas a um IEC."""

    def __init__(self, evidence_store):
        if evidence_store is None:
            raise ValueError("ScientificEvidenceBridge requer um EvidenceStore")
        self.evidence_store = evidence_store

    @staticmethod
    def evidence_id(result: Dict[str, Any]) -> str:
        """Gera um identificador estável para o mesmo resultado científico."""
        payload = json.dumps(result, sort_keys=True, default=str, ensure_ascii=False)
        digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()[:20]
        provider = str(result.get("provider", "unknown"))
        return f"scientific:{provider}:{digest}"

    def ingest(
        self,
        iec_id: str,
        result: Dict[str, Any],
        reliability: float | None = None,
    ) -> str:
        if not iec_id:
            raise ValueError("O IEC de destino é obrigatório")
        if not isinstance(result, dict):
            raise TypeError("O resultado científico deve ser um dicionário")

        evidence_id = self.evidence_id(result)
        provider = str(result.get("provider", "unknown"))
        if reliability is None:
            reliability = result.get("reliability", result.get("confidence", 0.5))

        self.evidence_store.add_evidence(
            evidence_id=evidence_id,
            content=dict(result),
            source_type=f"scientific:{provider}",
            reliability=float(reliability),
            provenance={
                "provider": provider,
                "query": result.get("query"),
                "external_id": result.get("doi") or result.get("id"),
                "url": result.get("url") or result.get("link"),
            },
        )
        self.evidence_store.link_to_iec(evidence_id, iec_id)
        return evidence_id

    def ingest_many(
        self,
        iec_id: str,
        results: Iterable[Dict[str, Any]],
        reliability: float | None = None,
    ) -> List[str]:
        return [
            self.ingest(iec_id, result, reliability=reliability)
            for result in results
        ]


__all__ = ["ScientificEvidenceBridge"]
