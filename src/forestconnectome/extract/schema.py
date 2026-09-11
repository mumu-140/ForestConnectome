from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


EntityType = str
AssertionStatus = Literal["observed", "inferred", "predicted", "hypothesized", "background"]
SpeciesScope = Literal["exact_species", "genus", "multi_species", "inferred_from_context", "unspecified"]
EvidenceType = Literal[
    "genetic",
    "biochemical",
    "binding",
    "expression",
    "phenotypic",
    "computational",
    "citation_only",
    "other",
]


class ExtractedEdge(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source: str
    source_type: EntityType
    relationship: str
    target: str
    target_type: EntityType
    species: str | None = None
    taxon_id: int | None = None
    species_scope: SpeciesScope = "unspecified"
    assertion_status: AssertionStatus
    evidence_type: EvidenceType = "other"
    relationship_basis: str | None = None
    evidence_text: str = Field(description="Verbatim source text that supports or contextualizes the edge")
    source_definition: str | None = None
    target_definition: str | None = None
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)


class ExtractionResult(BaseModel):
    model_config = ConfigDict(extra="forbid")
    edges: list[ExtractedEdge]
