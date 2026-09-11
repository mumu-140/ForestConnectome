from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional

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
    resolution_status: str = "unresolved"

@dataclass(slots=True)
class Provenance:
    source_id: str
    pmid: Optional[str] = None
    doi: Optional[str] = None
    chunk_id: Optional[str] = None
    evidence_text: Optional[str] = None
    extractor_version: Optional[str] = None

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
