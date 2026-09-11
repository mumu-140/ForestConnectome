from forestconnectome.resolve.aliases import GeneAliasIndex, GeneRecord


def test_aliases_do_not_cross_taxa():
    index = GeneAliasIndex([
        GeneRecord(3702, "AT5G12870", "Arabidopsis thaliana", symbol="MYB46", aliases=("MYB46",)),
        GeneRecord(3694, "Potri.X", "Populus trichocarpa", symbol="MYB46", aliases=("MYB46",)),
    ])
    assert index.resolve("MYB46", 3702).record.canonical_gene_id == "AT5G12870"
    assert index.resolve("MYB46", 3694).record.canonical_gene_id == "Potri.X"
