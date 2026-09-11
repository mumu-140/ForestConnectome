from forestconnectome.benchmark.schema import GoldEdge, read_gold_jsonl, write_gold_jsonl


def test_gold_benchmark_round_trip(tmp_path):
    row = GoldEdge(
        benchmark_id="B001",
        pmid="22236040",
        evidence_text="example",
        subject_label="KNAT7",
        predicate="INVOLVED_IN",
        object_label="secondary cell wall biosynthesis",
        subject_taxon_id=3702,
        object_taxon_id=None,
        assertion_status="observed",
        study_role="current_result",
        polarity="affirmed",
        evidence_type="genetic",
        extraction_decision="accept",
        expected_transfer_disposition="review_candidate",
        transfer_gold="conserved",
    )
    path = tmp_path / "gold.jsonl"
    write_gold_jsonl([row], path)
    assert read_gold_jsonl(path) == [row]
