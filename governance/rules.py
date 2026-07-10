"""governance/rules.py — Regras epistemológicas (3.0)."""

MIN_EDGE_WEIGHT = 0.4
MIN_SIMILARITY = 0.5


def is_valid_connection(score: float) -> bool:
    return score >= MIN_EDGE_WEIGHT
