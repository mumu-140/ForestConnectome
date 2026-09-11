from forestconnectome.extract.schema import ExtractedEdge, TaxonContext
from forestconnectome.resolve.entities import edge_to_claim


def make_edge(taxon_id, species):
    return ExtractedEdge(
        source="GENE1",
        source_type="gene",
        source_species=species,
        source_taxon_id=taxon_id,
        relationship="is involved in",
        target="secondary growth",
        target_type="process",
        target_species=None,
        target_taxon_id=None,
        study_taxa=[TaxonContext(species=species, taxon_id=taxon_id, role="experimental")],
        species_scope="exact_species",
        assertion_status="observed",
        study_role="current_result",
        polarity="affirmed",
        evidence_type="genetic",
        relationship_basis=None,
        evidence_text="GENE1 is involved in secondary growth.",
        source_definition=None,
        target_definition=None,
        model_confidence_raw=0.8,
    )


def test_process_identity_is_shared_across_species_contexts():
    at = edge_to_claim(make_edge(3702, "Arabidopsis thaliana"), source_id="a", chunk_id="a:0", section="abstract")
    pt = edge_to_claim(make_edge(3694, "Populus trichocarpa"), source_id="b", chunk_id="b:0", section="abstract")
    assert at.object.entity_id == pt.object.entity_id
    assert at.object.taxon_id is None
    assert pt.object.taxon_id is None
    assert at.subject.entity_id != pt.subject.entity_id


def test_cross_species_endpoints_keep_independent_taxa():
    edge = ExtractedEdge(
        source="AT1G01010",
        source_type="gene",
        source_species="Arabidopsis thaliana",
        source_taxon_id=3702,
        relationship="is orthologous to",
        target="Potri.001G000100",
        target_type="gene",
        target_species="Populus trichocarpa",
        target_taxon_id=3694,
        study_taxa=[
            TaxonContext(species="Arabidopsis thaliana", taxon_id=3702, role="computational"),
            TaxonContext(species="Populus trichocarpa", taxon_id=3694, role="computational"),
        ],
        species_scope="multi_species",
        assertion_status="inferred",
        study_role="current_result",
        polarity="affirmed",
        evidence_type="computational",
        evidence_text="AT1G01010 is orthologous to Potri.001G000100.",
    )
    claim = edge_to_claim(edge, source_id="x", chunk_id="x:0", section="results")
    assert claim.subject.taxon_id == 3702
    assert claim.object.taxon_id == 3694
    assert {ctx.taxon_id for ctx in claim.study_taxa} == {3702, 3694}
