from forestconnectome.ontology.taxon_constraints import GoTaxonConstraintIndex, TaxonConstraint


def test_only_in_taxon_passes_when_required_ancestor_is_in_lineage():
    index = GoTaxonConstraintIndex([TaxonConstraint("GO:1", "only_in_taxon", "NCBITaxon:33090")])
    decision = index.evaluate("GO:1", taxon_id=3694, lineage_taxon_ids={3694, 33090, 3193})
    assert decision.status == "pass"


def test_only_in_taxon_fails_outside_required_lineage():
    index = GoTaxonConstraintIndex([TaxonConstraint("GO:1", "only_in_taxon", "NCBITaxon:33090")])
    decision = index.evaluate("GO:1", taxon_id=9606, lineage_taxon_ids={9606, 40674})
    assert decision.status == "fail"


def test_never_in_taxon_blocks_descendant():
    index = GoTaxonConstraintIndex([TaxonConstraint("GO:1", "never_in_taxon", "NCBITaxon:40674")])
    decision = index.evaluate("GO:1", taxon_id=9606, lineage_taxon_ids={9606, 40674})
    assert decision.status == "fail"
    assert "go_never_in_taxon" in decision.reason_codes


def test_unknown_union_grouping_never_becomes_pass():
    index = GoTaxonConstraintIndex([TaxonConstraint("GO:1", "only_in_taxon", "NCBITaxon_Union:0000001")])
    decision = index.evaluate("GO:1", taxon_id=3694, lineage_taxon_ids={3694, 33090})
    assert decision.status == "unknown"


def test_union_grouping_can_be_resolved_by_explicit_membership():
    index = GoTaxonConstraintIndex([TaxonConstraint("GO:1", "only_in_taxon", "NCBITaxon_Union:0000001")])
    decision = index.evaluate(
        "GO:1",
        taxon_id=3694,
        lineage_taxon_ids={3694, 33090},
        grouping_members={"NCBITaxon_Union:0000001": {33090}},
    )
    assert decision.status == "pass"
