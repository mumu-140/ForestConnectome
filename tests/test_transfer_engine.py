from forestconnectome.models import Claim, Entity, Provenance
from forestconnectome.transfer.engine import GeneTransfer, transfer_claim
from forestconnectome.transfer.policy import OrthologyEvidence


def test_reference_claim_transfers_as_predicted_not_direct():
    at = Entity("gene:3702:TAIR10:AT1", "gene", "AT1", taxon_id=3702, canonical_gene_id="AT1")
    process = Entity("entity:global:process:x", "process", "secondary growth")
    source = Claim(
        "claim:at",
        at,
        "INVOLVED_IN",
        process,
        "direct",
        "observed",
        Provenance("PMID:1", pmid="1", evidence_text="AT1 is involved in secondary growth."),
        confidence=0.95,
    )
    pt = Entity("gene:3694:v4.1:Potri.X", "gene", "Potri.X", taxon_id=3694, canonical_gene_id="Potri.X")
    mapping = GeneTransfer(
        at.entity_id,
        pt,
        OrthologyEvidence("one_to_one", synteny_support=True, phylogenetic_support=0.95),
        3702,
        3694,
        "OG1",
    )
    transferred = transfer_claim(source, {at.entity_id: mapping})
    assert transferred is not None
    assert transferred.evidence_origin == "orthology_transfer"
    assert transferred.assertion_status == "predicted"
    assert transferred.transfer.source_claim_id == source.claim_id
    assert len(transferred.transfer.mappings) == 1
    assert transferred.transfer.mappings[0].orthogroup_id == "OG1"
    assert transferred.subject.entity_id == pt.entity_id
