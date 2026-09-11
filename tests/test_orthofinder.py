from forestconnectome.reference.orthofinder import parse_duplications_tsv, parse_orthologues_tsv


def test_parse_pairwise_orthologues_preserves_multiplicity(tmp_path):
    path = tmp_path / "Arabidopsis__v__Populus.tsv"
    path.write_text(
        "Orthogroup\tArabidopsis\tPopulus\n"
        "OG0001\tAT1G01010\tPotri.001G000100\n"
        "OG0002\tAT2G02020\tPotri.002G000200, Potri.002G000300\n",
        encoding="utf-8",
    )
    rows = parse_orthologues_tsv(path)
    assert rows[0].orthology_type == "one_to_one"
    one_to_many = [row for row in rows if row.orthogroup_id == "OG0002"]
    assert len(one_to_many) == 2
    assert all(row.orthology_type == "one_to_many" for row in one_to_many)
    assert all(row.duplication_risk for row in one_to_many)


def test_parse_duplication_events(tmp_path):
    path = tmp_path / "Duplications.tsv"
    path.write_text(
        "Orthogroup\tSpecies Tree node\tGene tree node\tSupport\tType\tGenes 1\tGenes 2\n"
        "OG0002\tPopulus\tn7\t0.93\tTerminal\tPotri.002G000200\tPotri.002G000300\n",
        encoding="utf-8",
    )
    row = parse_duplications_tsv(path)[0]
    assert row.support == 0.93
    assert row.duplication_type == "Terminal"
    assert row.genes_1 == ("Potri.002G000200",)
