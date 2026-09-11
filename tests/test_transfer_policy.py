from forestconnectome.transfer.policy import OrthologyEvidence, classify_transfer, evaluate_transfer


def _decision(**overrides):
    values = dict(
        predicate="INVOLVED_IN",
        orthology_tier="T1",
        source_assertion_status="observed",
        source_study_role="current_result",
        source_evidence_type="genetic",
        source_polarity="affirmed",
        taxon_constraint_status="pass",
        term_specificity="broad",
    )
    values.update(overrides)
    return evaluate_transfer(**values)


def test_t1_requires_one_to_one_and_strong_support():
    e = OrthologyEvidence("one_to_one", synteny_support=True, phylogenetic_support=0.9)
    assert classify_transfer(e) == "T1"


def test_t2_is_not_automatic_even_when_phylogenetically_supported():
    e = OrthologyEvidence("one_to_many", phylogenetic_support=0.95)
    assert classify_transfer(e) == "T2"
    assert _decision(orthology_tier="T2").disposition == "review_candidate"


def test_similarity_only_is_blocked():
    e = OrthologyEvidence("homology_only", sequence_support=0.99)
    assert classify_transfer(e) == "T4"
    assert _decision(orthology_tier="T4").disposition == "blocked"


def test_regulatory_edge_is_never_auto_from_orthology_alone():
    decision = _decision(predicate="REGULATES_POSITIVELY")
    assert decision.disposition == "review_candidate"
    assert "predicate_requires_direct_conservation_evidence" in decision.reason_codes


def test_broad_function_can_be_auto_candidate_only_after_all_gates_pass():
    assert _decision().disposition == "automatic_candidate"


def test_unknown_taxon_constraint_blocks_automatic_function_transfer():
    decision = _decision(taxon_constraint_status="unknown")
    assert decision.disposition == "review_candidate"


def test_inferred_or_prior_work_source_is_never_automatic():
    assert _decision(source_assertion_status="inferred").disposition == "review_candidate"
    assert _decision(source_study_role="prior_work").disposition == "review_candidate"


def test_expression_only_source_is_not_auto_transfer_grade():
    decision = _decision(source_evidence_type="expression")
    assert decision.disposition == "review_candidate"
    assert "source_evidence_not_auto_transfer_grade" in decision.reason_codes
