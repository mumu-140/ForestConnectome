from forestconnectome.models import Entity
from forestconnectome.ontology.grounding import OntologyIndex, OntologyTermRecord, apply_grounding
from forestconnectome.ontology.registry import OntologyRegistry


def _go_index():
    return OntologyIndex(
        "GO",
        [
            OntologyTermRecord(
                "GO:0009832",
                "plant-type cell wall biogenesis",
                synonyms=("plant cell wall biogenesis",),
                definition="The assembly of a plant-type cell wall.",
            ),
            OntologyTermRecord("GO:0003674", "molecular function"),
        ],
    )


def test_exact_label_grounding_uses_authoritative_identifier():
    result = _go_index().ground("plant-type cell wall biogenesis")
    assert result.status == "exact_label"
    assert result.term_id == "GO:0009832"


def test_exact_synonym_grounding_is_explicit():
    result = _go_index().ground("plant cell wall biogenesis")
    assert result.status == "exact_synonym"
    entity = Entity("tmp", "biological process", "plant cell wall biogenesis")
    grounded = apply_grounding(entity, result)
    assert grounded.canonical_ontology_id == "GO:0009832"
    assert grounded.entity_id == "ontology:GO:0009832"
    assert grounded.label == "plant cell wall biogenesis"
    assert grounded.resolution_status == "alias_resolved"


def test_registry_routes_concepts_but_not_genes():
    registry = OntologyRegistry({"GO": _go_index()})
    process = Entity("tmp", "biological process", "plant cell wall biogenesis")
    gene = Entity("gene:3702:x:AT5G12870", "gene", "MYB46", taxon_id=3702, canonical_gene_id="AT5G12870")
    grounded, result = registry.ground_entity(process)
    same_gene, gene_result = registry.ground_entity(gene)
    assert grounded.canonical_ontology_id == "GO:0009832"
    assert result is not None and result.resolved
    assert same_gene is gene
    assert gene_result is None


def test_ambiguous_synonym_is_not_silently_resolved():
    index = OntologyIndex(
        "GO",
        [
            OntologyTermRecord("GO:1", "alpha", synonyms=("shared",)),
            OntologyTermRecord("GO:2", "beta", synonyms=("shared",)),
        ],
    )
    result = index.ground("shared")
    assert result.status == "ambiguous"
    assert set(result.candidates) == {"GO:1", "GO:2"}
