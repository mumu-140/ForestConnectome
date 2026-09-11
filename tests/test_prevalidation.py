from forestconnectome.extract.schema import ExtractedEdge
from forestconnectome.ingest.chunking import TextChunk
from forestconnectome.validate.rules import prevalidate_edge


def _edge(**overrides):
    values = dict(
        source="A",
        source_type="gene",
        relationship="regulates",
        target="B",
        target_type="gene",
        assertion_status="observed",
        study_role="current_result",
        polarity="affirmed",
        evidence_text="A regulates B.",
    )
    values.update(overrides)
    return ExtractedEdge(**values)


def test_hypothesis_is_routed_to_review():
    chunk = TextChunk("p1", "p1:discussion:0000", "discussion", "We asked whether A regulates B.", 0, 29)
    edge = _edge(assertion_status="hypothesized", evidence_text="We asked whether A regulates B.")
    decision = prevalidate_edge(edge, chunk)
    assert decision.status == "review"
    assert "hypothesis_not_direct_fact" in decision.reasons


def test_prior_work_is_separate_from_assertion_status_and_reviewed():
    chunk = TextChunk("p1", "p1:intro:0000", "introduction", "Previous work showed A regulates B.", 0, 34)
    edge = _edge(study_role="prior_work", evidence_text="Previous work showed A regulates B.")
    decision = prevalidate_edge(edge, chunk)
    assert edge.assertion_status == "observed"
    assert decision.status == "review"
    assert "study_role_prior_work" in decision.reasons


def test_negated_edge_is_not_accepted_as_positive_fact():
    chunk = TextChunk("p1", "p1:results:0000", "results", "A does not regulate B.", 0, 22)
    edge = _edge(polarity="negated", evidence_text="A does not regulate B.")
    decision = prevalidate_edge(edge, chunk)
    assert decision.status == "review"
    assert "polarity_negated" in decision.reasons
