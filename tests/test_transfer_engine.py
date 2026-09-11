from forestconnectome.models import Claim, Entity, Provenance, TaxonContext
from forestconnectome.transfer.engine import GeneTransfer, transfer_claim
from forestconnectome.transfer.policy import OrthologyEvidence


def _source_claim(predicate="INVOLVED_IN"):
    at = Entity("gene:3702:TAIR10:AT1", "gene", "AT1", taxon_id=3702, canonical_gene_id="AT1")
    process = Entity("entity:global:process:x", "process", "secondary growth")
    source = Claim(
        "claim:at",
        at,
        predicate,
        process,
        "direct",
        "observed",
        Provenance("PMID:1", pmid="1", evidence_text="AT1 is involved in secondary growth."),
        study_role="current_result",
        polarity="affirmed",
        study_taxa=[TaxonContext("Arabidopsis thaliana", 3702, "experimental")],
        evidence_type="genetic",
        model_confidence_raw=0.99,
        calibrated_confidence=0.91,
    )
    return source, at


def _t1_mapping(at):
    pt = Entity("gene:3694:v4.1:Potri.X", "gene", "Potri.X", taxon_id=3694, canonical_gene_id="Potri.X")
    mapping = GeneTransfer(
        at.entity_id,
        pt,
        OrthologyEvidence("one_to_one", synteny_support=True, phylogenetic_support=0.95),
        3702,
        3694,
        "OG1",
    )
    return mapping, pt


def test_reference_function_claim_transfers_as_predicted_not_direct():
    source, at = _source_claim()
    mapping, pt = _t1_mapping(at)
    transferred = transfer_claim(
        source,
        {at.entity_id: mapping},
        taxon_constraint_status="pass",
        term_specificity="broad",
    )
    assert transferred is not None
    assert transferred.evidence_origin == "orthology_transfer"
    assert transferred.assertion_status == "predicted"
    assert transferred.study_role == "derived_transfer"
    assert transferred.evidence_type == "computational"
    assert transferred.study_taxa == []
    assert transferred.species_scope == "unspecified"
    assert transferred.model_confidence_raw is None
    assert transferred.calibrated_confidence is None
    assert transferred.transfer.source_evidence_type == "genetic"
    assert transferred.transfer.source_model_confidence_raw == 0.99
    assert transferred.transfer.source_calibrated_confidence == 0.91
    assert transferred.transfer.transfer_disposition == "automatic_candidate"
    assert transferred.transfer.source_claim_id == source.claim_id
    assert len(transferred.transfer.mappings) == 1
    assert transferred.transfer.mappings[0].orthogroup_id == "OG1"
    assert transferred.subject.entity_id == pt.entity_id


def test_t1_regulatory_claim_is_not_automatic_but_can_be_review_candidate():
    source, at = _source_claim(predicate="REGULATES_POSITIVELY")
    mapping, _ = _t1_mapping(at)
    assert transfer_claim(
        source,
        {at.entity_id: mapping},
        taxon_constraint_status="pass",
        term_specificity="broad",
    ) is None

    candidate = transfer_claim(
        source,
        {at.entity_id: mapping},
        require_automatic=False,
        taxon_constraint_status="pass",
        term_specificity="broad",
    )
    assert candidate is not None
    assert candidate.transfer.transfer_disposition == "review_candidate"
    assert candidate.evidence_type == "computational"


def test_transferred_claim_cannot_be_cascaded_to_another_species():
    source, at = _source_claim()
    mapping, _ = _t1_mapping(at)
    first = transfer_claim(
        source,
        {at.entity_id: mapping},
        taxon_constraint_status="pass",
        term_specificity="broad",
    )
    assert first is not None
    assert transfer_claim(first, {}) is None


def test_transfer_engine_can_resolve_go_taxon_constraint_from_grounded_term():
    from forestconnectome.ontology.taxon_constraints import GoTaxonConstraintIndex, TaxonConstraint

    source, at = _source_claim()
    source.object.canonical_ontology_id = "GO:0009832"
    source.object.ontology_prefix = "GO"
    mapping, _ = _t1_mapping(at)
    constraints = GoTaxonConstraintIndex(
        [TaxonConstraint("GO:0009832", "only_in_taxon", "NCBITaxon:33090")]
    )
    transferred = transfer_claim(
        source,
        {at.entity_id: mapping},
        go_taxon_constraints=constraints,
        target_lineage_taxon_ids={3694, 33090, 3193},
        term_specificity="broad",
    )
    assert transferred is not None
    assert transferred.transfer.taxon_constraint_status == "pass"


def test_transfer_engine_blocks_go_taxon_constraint_mismatch():
    from forestconnectome.ontology.taxon_constraints import GoTaxonConstraintIndex, TaxonConstraint

    source, at = _source_claim()
    source.object.canonical_ontology_id = "GO:0009832"
    source.object.ontology_prefix = "GO"
    mapping, _ = _t1_mapping(at)
    constraints = GoTaxonConstraintIndex(
        [TaxonConstraint("GO:0009832", "never_in_taxon", "NCBITaxon:33090")]
    )
    assert transfer_claim(
        source,
        {at.entity_id: mapping},
        go_taxon_constraints=constraints,
        target_lineage_taxon_ids={3694, 33090, 3193},
        term_specificity="broad",
    ) is None
