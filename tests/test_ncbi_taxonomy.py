from forestconnectome.reference.ncbi_taxonomy import lineage_ids_from_record


def test_lineage_ids_include_self_and_ancestors():
    record = {
        "TaxId": "3694",
        "LineageEx": [{"TaxId": "33090"}, {"TaxId": "3193"}],
    }
    assert lineage_ids_from_record(record) == {3694, 33090, 3193}
