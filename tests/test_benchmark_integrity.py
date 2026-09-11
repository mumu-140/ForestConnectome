from pathlib import Path

import pytest

from forestconnectome.benchmark.schema import GoldEdge, read_gold_jsonl, validate_benchmark_integrity


def test_repository_gold_seed_is_valid_and_contains_positive_and_negative_transfer_examples():
    path = Path(__file__).parents[1] / "data" / "benchmark" / "gold_seed.jsonl"
    rows = read_gold_jsonl(path)
    validate_benchmark_integrity(rows)
    assert len(rows) >= 8
    assert {row.transfer_gold for row in rows} >= {"conserved", "diverged", "uncertain"}
    assert all(row.evidence_text for row in rows)


def test_benchmark_rejects_pmid_split_leakage():
    common = dict(
        evidence_text="evidence",
        subject_label="A",
        predicate="INVOLVED_IN",
        object_label="B",
        subject_taxon_id=3702,
        object_taxon_id=None,
        assertion_status="observed",
        study_role="current_result",
        polarity="affirmed",
        evidence_type="genetic",
        extraction_decision="accept",
    )
    rows = [
        GoldEdge("B1", "1", split="train", **common),
        GoldEdge("B2", "1", split="test", **common),
    ]
    with pytest.raises(ValueError, match="PMID split leakage"):
        validate_benchmark_integrity(rows)
