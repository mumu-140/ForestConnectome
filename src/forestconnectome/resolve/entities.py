from __future__ import annotations

from forestconnectome.extract.schema import ExtractedEdge
from forestconnectome.ids import make_claim_id, make_entity_id
from forestconnectome.models import Claim, Entity, Provenance, TaxonContext
from forestconnectome.resolve.aliases import GeneAliasIndex
from forestconnectome.resolve.relations import normalize_relation

_GENE_LIKE = {"gene", "gene identifier", "protein", "transcription factor", "enzyme"}


def _resolve_entity(
    label: str,
    entity_type: str,
    *,
    taxon_id: int | None,
    species: str | None,
    definition: str | None,
    alias_index: GeneAliasIndex | None,
) -> Entity:
    normalized_type = entity_type.strip().lower()
    canonical_gene_id = None
    symbol = None
    aliases: list[str] = []
    genome_build = None
    status = "not_applicable"

    if normalized_type in _GENE_LIKE:
        status = "unresolved"
        if taxon_id is not None and alias_index is not None:
            result = alias_index.resolve(label, taxon_id)
            status = result.status
            if result.record is not None:
                canonical_gene_id = result.record.canonical_gene_id
                symbol = result.record.symbol
                aliases = list(result.record.aliases)
                genome_build = result.record.genome_build
                species = result.record.species

    identity_taxon = taxon_id if normalized_type in _GENE_LIKE else None
    identity_species = species if normalized_type in _GENE_LIKE else None
    entity_id = make_entity_id(
        entity_type=normalized_type,
        label=label,
        taxon_id=identity_taxon,
        genome_build=genome_build,
        canonical_gene_id=canonical_gene_id,
    )
    return Entity(
        entity_id=entity_id,
        entity_type=normalized_type,
        label=label,
        taxon_id=identity_taxon,
        species=identity_species,
        genome_build=genome_build,
        canonical_gene_id=canonical_gene_id,
        symbol=symbol,
        aliases=aliases,
        definition=definition,
        resolution_status=status,
    )


def _single_study_taxon(edge: ExtractedEdge) -> tuple[int | None, str | None]:
    """Return a unique study taxon only when one unambiguous taxon is present."""
    usable = [(item.taxon_id, item.species) for item in edge.study_taxa if item.taxon_id is not None or item.species]
    unique = list(dict.fromkeys(usable))
    return unique[0] if len(unique) == 1 else (None, None)


def edge_to_claim(
    edge: ExtractedEdge,
    *,
    source_id: str,
    chunk_id: str,
    section: str,
    pmid: str | None = None,
    doi: str | None = None,
    alias_index: GeneAliasIndex | None = None,
    extractor_version: str | None = None,
    model: str | None = None,
) -> Claim:
    relation = normalize_relation(edge.relationship)

    fallback_taxon, fallback_species = _single_study_taxon(edge)
    source_taxon = edge.source_taxon_id if edge.source_taxon_id is not None else fallback_taxon
    source_species = edge.source_species if edge.source_species is not None else fallback_species
    target_taxon = edge.target_taxon_id if edge.target_taxon_id is not None else fallback_taxon
    target_species = edge.target_species if edge.target_species is not None else fallback_species

    subject = _resolve_entity(
        edge.source,
        edge.source_type,
        taxon_id=source_taxon,
        species=source_species,
        definition=edge.source_definition,
        alias_index=alias_index,
    )
    obj = _resolve_entity(
        edge.target,
        edge.target_type,
        taxon_id=target_taxon,
        species=target_species,
        definition=edge.target_definition,
        alias_index=alias_index,
    )
    if relation.reverse:
        subject, obj = obj, subject

    provenance = Provenance(
        source_id=source_id,
        pmid=pmid,
        doi=doi,
        chunk_id=chunk_id,
        section=section,
        evidence_text=edge.evidence_text,
        relationship_basis=edge.relationship_basis,
        extractor_version=extractor_version,
        model=model,
    )
    claim_id = make_claim_id(
        subject_id=subject.entity_id,
        predicate=relation.canonical,
        object_id=obj.entity_id,
        source_id=source_id,
        chunk_id=chunk_id,
        evidence_text=edge.evidence_text,
    )
    return Claim(
        claim_id=claim_id,
        subject=subject,
        predicate=relation.canonical,
        object=obj,
        evidence_origin="direct",
        assertion_status=edge.assertion_status,
        provenance=provenance,
        study_role=edge.study_role,
        polarity=edge.polarity,
        study_taxa=[TaxonContext(item.species, item.taxon_id, item.role) for item in edge.study_taxa],
        evidence_type=edge.evidence_type,
        species_scope=edge.species_scope,
        model_confidence_raw=edge.model_confidence_raw,
        calibrated_confidence=None,
    )
