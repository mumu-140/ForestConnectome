from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Optional


@dataclass(slots=True)
class Entity:
    entity_id: str
    entity_type: str
    label: str
    taxon_id: Optional[int] = None
    species: Optional[str] = None
    genome_build: Optional[str] = None
    canonical_gene_id: Optional[str] = None
    symbol: Optional[str] = None
    aliases: list[str] = field(default_factory=list)
    definition: Optional[str] = None
    resolution_status: str = "unresolved"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class Provenance:
    source_id: str
    pmid: Optional[str] = None
    doi: Optional[str] = None
    chunk_id: Optional[str] = None
    section: Optional[str] = None
    evidence_text: Optional[str] = None
    relationship_basis: Optional[str] = None
    extractor_version: Optional[str] = None
    model: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class EntityTransferMetadata:
    source_entity_id: str
    target_entity_id: str
    source_taxon_id: int
    target_taxon_id: int
    orthology_type: str
    orthogroup_id: Optional[str] = None
    synteny_support: Optional[bool] = None
    phylogenetic_support: Optional[float] = None
    sequence_support: Optional[float] = None
    expression_support: Optional[float] = None


@dataclass(slots=True)
class TransferMetadata:
    source_claim_id: str
    source_taxon_id: int
    target_taxon_id: int
    transfer_tier: str
    transfer_confidence: float
    mappings: list[EntityTransferMetadata] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class Claim:
    claim_id: str
    subject: Entity
    predicate: str
    object: Entity
    evidence_origin: str
    assertion_status: str
    provenance: Provenance
    evidence_type: str = "other"
    species_scope: str = "unspecified"
    confidence: float = 0.0
    transfer: Optional[TransferMetadata] = None

    def to_dict(self) -> dict[str, Any]:
        value = asdict(self)
        if self.transfer is None:
            value.pop("transfer", None)
        return value
