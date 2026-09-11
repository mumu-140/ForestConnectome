from __future__ import annotations

from dataclasses import dataclass
from math import sqrt
from typing import Iterable


@dataclass(frozen=True, slots=True)
class TypeCandidate:
    entity_type: str
    similarity: float


def cosine_similarity(a: list[float], b: list[float]) -> float:
    if len(a) != len(b):
        raise ValueError("embedding dimensions differ")
    dot = sum(x * y for x, y in zip(a, b))
    na = sqrt(sum(x * x for x in a))
    nb = sqrt(sum(y * y for y in b))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


def top_type_candidates(
    query_embedding: list[float],
    references: Iterable[tuple[str, list[float]]],
    *,
    top_k: int = 10,
) -> list[TypeCandidate]:
    ranked = [TypeCandidate(name, cosine_similarity(query_embedding, emb)) for name, emb in references]
    ranked.sort(key=lambda item: item.similarity, reverse=True)
    return ranked[:top_k]
