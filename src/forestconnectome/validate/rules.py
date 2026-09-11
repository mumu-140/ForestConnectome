from __future__ import annotations

from dataclasses import dataclass

from forestconnectome.extract.schema import ExtractedEdge
from forestconnectome.ingest.chunking import TextChunk


@dataclass(frozen=True, slots=True)
class ValidationDecision:
    status: str
    reasons: tuple[str, ...]


def prevalidate_edge(edge: ExtractedEdge, chunk: TextChunk) -> ValidationDecision:
    reasons: list[str] = []
    status = "accept"

    if edge.evidence_text not in chunk.text:
        reasons.append("evidence_text_not_verbatim")
        status = "review"
    if edge.assertion_status == "hypothesized":
        reasons.append("hypothesis_not_direct_fact")
        status = "review"
    if edge.assertion_status == "background":
        reasons.append("background_or_prior_literature")
        status = "review"
    if not edge.source.strip() or not edge.target.strip() or not edge.relationship.strip():
        reasons.append("missing_edge_component")
        status = "reject"

    return ValidationDecision(status, tuple(reasons))
