from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


EntityType = str
AssertionStatus = Literal["observed", "inferred", "predicted", "hypothesized"]
StudyRole = Literal[
    "current_result",
    "prior_work",
    "review_statement",
    "discussion_interpretation",
    "unknown",
]
Polarity = Literal["affirmed", "negated", "uncertain"]
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
TaxonRole = Literal["experimental", "computational", "host", "described", "other"]


class TaxonContext(BaseModel):
    """A taxon that belongs to the evidence/study context, not necessarily both edge endpoints."""

    model_config = ConfigDict(extra="forbid")

    species: str | None = None
    taxon_id: int | None = None
    role: TaxonRole = "described"


class ExtractedEdge(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source: str
    source_type: EntityType
    source_species: str | None = None
    source_taxon_id: int | None = None
    relationship: str
    target: str
    target_type: EntityType
    target_species: str | None = None
    target_taxon_id: int | None = None

    # Species/taxa that supplied the evidence. These are kept separate from the
    # taxonomic identity of source/target entities so cross-species statements are representable.
    study_taxa: list[TaxonContext] = Field(default_factory=list)
    species_scope: SpeciesScope = "unspecified"

    # Orthogonal statement dimensions. "Prior work" is not an assertion status,
    # and a negated statement must not be silently stored as an affirmed edge.
    assertion_status: AssertionStatus
    study_role: StudyRole = "unknown"
    polarity: Polarity = "affirmed"

    evidence_type: EvidenceType = "other"
    relationship_basis: str | None = None
    evidence_text: str = Field(description="Smallest verbatim source span sufficient to audit the edge")
    source_definition: str | None = None
    target_definition: str | None = None

    # This is only the model's self-assessment. It is not a calibrated probability
    # and must not be used directly as scientific confidence or transfer confidence.
    model_confidence_raw: float | None = Field(default=None, ge=0.0, le=1.0)


class ExtractionResult(BaseModel):
    model_config = ConfigDict(extra="forbid")
    edges: list[ExtractedEdge]
