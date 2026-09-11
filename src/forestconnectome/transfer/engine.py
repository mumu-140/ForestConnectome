from __future__ import annotations

from dataclasses import dataclass

from forestconnectome.ids import make_claim_id
from forestconnectome.models import Claim, Entity, EntityTransferMetadata, Provenance, TransferMetadata
from forestconnectome.transfer.policy import (
    OrthologyEvidence,
    TaxonConstraintStatus,
    TermSpecificity,
    classify_transfer,
    evaluate_transfer,
)


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
    require_automatic: bool = True,
    taxon_constraint_status: TaxonConstraintStatus = "unknown",
    term_specificity: TermSpecificity = "unknown",
) -> Claim | None:
    """Project a reference claim without conflating orthology with edge conservation."""
    if claim.evidence_origin != "direct":
        return None

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
    tier = max(tiers, key=lambda x: int(x[1:]))
    decision = evaluate_transfer(
        predicate=claim.predicate,
        orthology_tier=tier,
        source_assertion_status=claim.assertion_status,
        source_study_role=claim.study_role,
        source_evidence_type=claim.evidence_type,
        source_polarity=claim.polarity,
        taxon_constraint_status=taxon_constraint_status,
        term_specificity=term_specificity,
    )
    if decision.disposition == "blocked":
        return None
    if require_automatic and decision.disposition != "automatic_candidate":
        return None

    subject = source_map.target if source_map else claim.subject
    obj = object_map.target if object_map else claim.object

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
        transfer_disposition=decision.disposition,
        reason_codes=list(decision.reason_codes),
        taxon_constraint_status=taxon_constraint_status,
        term_specificity=term_specificity,
        source_evidence_type=claim.evidence_type,
        source_assertion_status=claim.assertion_status,
        source_study_role=claim.study_role,
        source_model_confidence_raw=claim.model_confidence_raw,
        source_calibrated_confidence=claim.calibrated_confidence,
        mappings=entity_mappings,
    )
    target_assertion = "hypothesized" if decision.disposition == "hypothesis_only" else "predicted"
    return Claim(
        claim_id=transferred_id,
        subject=subject,
        predicate=claim.predicate,
        object=obj,
        evidence_origin="orthology_transfer",
        assertion_status=target_assertion,
        provenance=provenance,
        study_role="derived_transfer",
        polarity="affirmed",
        study_taxa=[],
        evidence_type="computational",
        species_scope="unspecified",
        model_confidence_raw=None,
        calibrated_confidence=None,
        transfer=meta,
    )
