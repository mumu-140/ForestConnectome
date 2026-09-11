from __future__ import annotations

import os
from typing import Iterable

from forestconnectome.models import Entity


def entity_embedding_text(entity: Entity) -> str:
    """PlantConnectome-compatible semantic payload, augmented with explicit taxon identity."""
    parts = [
        entity.label,
        f"type={entity.entity_type}",
        f"taxon={entity.taxon_id}" if entity.taxon_id is not None else None,
        f"gene_id={entity.canonical_gene_id}" if entity.canonical_gene_id else None,
        f"definition={entity.definition}" if entity.definition else None,
    ]
    return " | ".join(part for part in parts if part)


def embed_texts(
    texts: Iterable[str],
    *,
    model: str = "text-embedding-3-large",
    api_key: str | None = None,
) -> list[list[float]]:
    try:
        from openai import OpenAI
    except ImportError as exc:  # pragma: no cover - optional dependency
        raise RuntimeError("Install forestconnectome[llm] to generate embeddings") from exc
    client = OpenAI(api_key=api_key or os.environ.get("OPENAI_API_KEY"))
    response = client.embeddings.create(model=model, input=list(texts))
    return [item.embedding for item in response.data]
