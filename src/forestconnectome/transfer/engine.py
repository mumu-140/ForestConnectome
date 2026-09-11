from __future__ import annotations

from dataclasses import dataclass

from forestconnectome.ids import make_claim_id
from forestconnectome.models import Claim, Entity, EntityTransferMetadata, Provenance, TransferMetadata
from forestconnectome.transfer.policy import OrthologyEvidence, allows_automatic_transfer, classify_transfer


@dataclass(frozen=True, slots=True)
class GeneTransfer:
    source_entity_id: str
    target: Entity
    evidence: OrthologyEvidence
    source_taxon_id: int
    target_taxon_id: int
    orthogroup_id: str | None = None


def _is_gene_like(entity: Entity) -> bool:
    return entity.entity_type in {"gene", "gene identifier", "protein", "transcription factor", "enzyme"}


def transfer_claim(
    claim: Claim,
    mappings: dict[str, GeneTransfer],
    *,
    require_automatic_tier: bool = True,
) -> Claim | None:
    """Project a reference claim to a target taxon without erasing source evidence.

    Every gene-like endpoint must have a mapping. Shared concepts such as processes,
    tissues, phenotypes and chemicals are retained. Each mapped endpoint keeps its own
    orthology evidence because gene-gene edges generally involve two orthogroups.
    """
    source_map = mappings.get(claim.subject.entity_id) if _is_gene_like(claim.subject) else None
    object_map = mappings.get(claim.object.entity_id) if _is_gene_like(claim.object) else None
    if _is_gene_like(claim.subject) and source_map is None:
        return None
    if _is_gene_like(claim.object) and object_map is None:
        return None

    applicable = [m for m in (source_map, object_map) if m is not None]
    if not applicable:
        return None
    target_taxa = {m.target_taxon_id for m in applicable}
    source_taxa = {m.source_taxon_id for m in applicable}
    if len(target_taxa) != 1 or len(source_taxa) != 1:
        return None

    tiers = [classify_transfer(m.evidence) for m in applicable]
    tier = max(tiers, key=lambda x: int(x[1:]))  # weakest endpoint controls edge tier
    if require_automatic_tier and not allows_automatic_transfer(tier):
        return None

    subject = source_map.target if source_map else claim.subject
    obj = object_map.target if object_map else claim.object
    confidence_by_tier = {"T1": 0.9, "T2": 0.7, "T3": 0.4, "T4": 0.2}
    transfer_confidence = min(claim.confidence, confidence_by_tier[tier])

    provenance = Provenance(
        source_id=claim.provenance.source_id,
        pmid=claim.provenance.pmid,
        doi=claim.provenance.doi,
        chunk_id=claim.provenance.chunk_id,
        section=claim.provenance.section,
        evidence_text=claim.provenance.evidence_text,
        relationship_basis=claim.provenance.relationship_basis,
        extractor_version=claim.provenance.extractor_version,
        model=claim.provenance.model,
    )
    transferred_id = make_claim_id(
        subject_id=subject.entity_id,
        predicate=claim.predicate,
        object_id=obj.entity_id,
        source_id=f"transfer:{claim.claim_id}",
        chunk_id=claim.provenance.chunk_id,
        evidence_text=claim.provenance.evidence_text,
    )
    entity_mappings = [
        EntityTransferMetadata(
            source_entity_id=m.source_entity_id,
            target_entity_id=m.target.entity_id,
            source_taxon_id=m.source_taxon_id,
            target_taxon_id=m.target_taxon_id,
            orthology_type=m.evidence.orthology_type,
            orthogroup_id=m.orthogroup_id,
            synteny_support=m.evidence.synteny_support,
            phylogenetic_support=m.evidence.phylogenetic_support,
            sequence_support=m.evidence.sequence_support,
            expression_support=m.evidence.expression_support,
        )
        for m in applicable
    ]
    meta = TransferMetadata(
        source_claim_id=claim.claim_id,
        source_taxon_id=next(iter(source_taxa)),
        target_taxon_id=next(iter(target_taxa)),
        transfer_tier=tier,
        transfer_confidence=transfer_confidence,
        mappings=entity_mappings,
    )
    return Claim(
        claim_id=transferred_id,
        subject=subject,
        predicate=claim.predicate,
        object=obj,
        evidence_origin="orthology_transfer",
        assertion_status="predicted",
        provenance=provenance,
        evidence_type=claim.evidence_type,
        species_scope="exact_species",
        confidence=transfer_confidence,
        transfer=meta,
    )
