"""Normalização de resultados científicos externos."""

from typing import Any, Dict, Iterable, List


def normalize_result(item: Dict[str, Any], *, provider: str, query: str) -> Dict[str, Any]:
    if not isinstance(item, dict):
        raise TypeError("Resultado científico deve ser um dicionário")
    result = dict(item)
    result.setdefault("provider", provider)
    result.setdefault("query", query)
    return result


def normalize_results(items: Iterable[Dict[str, Any]] | None, *, provider: str, query: str) -> List[Dict[str, Any]]:
    return [normalize_result(item, provider=provider, query=query) for item in (items or [])]


__all__ = ["normalize_result", "normalize_results"]
