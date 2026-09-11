from forestconnectome.reference.ensembl import (
    EnsemblRestClient,
    canonicalize_populus_v41_gene_id,
    parse_homology_response,
)


def test_populus_ensembl_id_maps_to_phytozome_gene_id():
    assert canonicalize_populus_v41_gene_id("Potri.005G225400.v4.1") == "Potri.005G225400"
    assert canonicalize_populus_v41_gene_id("Potri.005G225400") == "Potri.005G225400"


def test_homology_parser_preserves_raw_evidence_and_is_conservative():
    payload = {
        "data": [
            {
                "id": "AT5G12870",
                "homologies": [
                    {
                        "type": "ortholog_one2many",
                        "taxonomy_level": "Malpighiales",
                        "confidence": 1,
                        "source": {"id": "AT5G12870", "species": "arabidopsis_thaliana", "perc_id": 62.0},
                        "target": {"id": "Potri.005G225400.v4.1", "species": "populus_trichocarpa", "perc_id": 60.0},
                    }
                ],
            }
        ]
    }
    record = parse_homology_response(payload)[0]
    assert record.target_id == "Potri.005G225400"
    assert record.orthology_type == "one_to_many"
    assert record.sequence_support == 0.6
    evidence = record.conservative_transfer_evidence()
    assert evidence.synteny_support is False
    assert evidence.phylogenetic_support == 0.0


def test_homology_url_requests_plant_compara():
    client = EnsemblRestClient()
    url = client._url(
        "homology/id/arabidopsis_thaliana/AT5G12870",
        {"target_species": "populus_trichocarpa", "type": "orthologues", "compara": "plants", "sequence": "none"},
    )
    assert "compara=plants" in url
    assert "target_species=populus_trichocarpa" in url
