from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from forestconnectome.extract.schema import ExtractionResult
from forestconnectome.ingest.chunking import TextChunk
from forestconnectome.models import Claim
from forestconnectome.resolve.aliases import GeneAliasIndex
from forestconnectome.resolve.entities import edge_to_claim
from forestconnectome.validate.rules import ValidationDecision, prevalidate_edge


class Extractor(Protocol):
    model: str

    def extract(self, chunk: TextChunk) -> ExtractionResult: ...


@dataclass(slots=True)
class ProcessedChunk:
    accepted_claims: list[Claim]
    review_claims: list[Claim]
    rejected_edges: list[tuple[int, ValidationDecision]]


def process_chunk(
    chunk: TextChunk,
    extractor: Extractor,
    *,
    alias_index: GeneAliasIndex | None = None,
    pmid: str | None = None,
    doi: str | None = None,
    extractor_version: str = "forestconnectome-v0.3",
) -> ProcessedChunk:
    result = extractor.extract(chunk)
    accepted: list[Claim] = []
    review: list[Claim] = []
    rejected: list[tuple[int, ValidationDecision]] = []

    for index, edge in enumerate(result.edges):
        decision = prevalidate_edge(edge, chunk)
        if decision.status == "reject":
            rejected.append((index, decision))
            continue

        claim = edge_to_claim(
            edge,
            source_id=chunk.source_id,
            chunk_id=chunk.chunk_id,
            section=chunk.section,
            pmid=pmid,
            doi=doi,
            alias_index=alias_index,
            extractor_version=extractor_version,
            model=extractor.model,
        )
        if decision.status == "accept":
            accepted.append(claim)
        else:
            review.append(claim)

    return ProcessedChunk(accepted, review, rejected)
