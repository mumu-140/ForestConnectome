from forestconnectome.extract.schema import ExtractedEdge
from forestconnectome.resolve.entities import edge_to_claim


def make_edge(taxon_id, species):
    return ExtractedEdge(
        source="GENE1",
        source_type="gene",
        relationship="is involved in",
        target="secondary growth",
        target_type="process",
        species=species,
        taxon_id=taxon_id,
        species_scope="exact_species",
        assertion_status="observed",
        evidence_type="genetic",
        relationship_basis=None,
        evidence_text="GENE1 is involved in secondary growth.",
        source_definition=None,
        target_definition=None,
        confidence=0.8,
    )


def test_process_identity_is_shared_across_species_contexts():
    at = edge_to_claim(make_edge(3702, "Arabidopsis thaliana"), source_id="a", chunk_id="a:0", section="abstract")
    pt = edge_to_claim(make_edge(3694, "Populus trichocarpa"), source_id="b", chunk_id="b:0", section="abstract")
    assert at.object.entity_id == pt.object.entity_id
    assert at.object.taxon_id is None
    assert pt.object.taxon_id is None
    assert at.subject.entity_id != pt.subject.entity_id
