from forestconnectome.extract.schema import ExtractedEdge
from forestconnectome.ingest.chunking import TextChunk
from forestconnectome.validate.rules import prevalidate_edge


def test_hypothesis_is_routed_to_review():
    chunk = TextChunk("p1", "p1:discussion:0000", "discussion", "We asked whether A regulates B.", 0, 29)
    edge = ExtractedEdge(
        source="A",
        source_type="gene",
        relationship="regulates",
        target="B",
        target_type="gene",
        assertion_status="hypothesized",
        evidence_text="We asked whether A regulates B.",
    )
    decision = prevalidate_edge(edge, chunk)
    assert decision.status == "review"
    assert "hypothesis_not_direct_fact" in decision.reasons
