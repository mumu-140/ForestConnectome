from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Literal

BenchmarkSplit = Literal["train", "dev", "test"]
GoldDecision = Literal["accept", "review", "reject"]
TransferGold = Literal["conserved", "diverged", "uncertain", "not_applicable"]
TransferDispositionGold = Literal["automatic_candidate", "review_candidate", "hypothesis_only", "blocked", "not_applicable"]


@dataclass(frozen=True, slots=True)
class GoldEdge:
    benchmark_id: str
    pmid: str
    evidence_text: str
    subject_label: str
    predicate: str
    object_label: str
    subject_taxon_id: int | None
    object_taxon_id: int | None
    assertion_status: str
    study_role: str
    polarity: str
    evidence_type: str
    extraction_decision: GoldDecision
    transfer_gold: TransferGold = "not_applicable"
    expected_transfer_disposition: TransferDispositionGold = "not_applicable"
    notes: str | None = None
    reviewer: str | None = None
    split: BenchmarkSplit = "dev"

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def write_gold_jsonl(records: list[GoldEdge], path: str | Path) -> None:
    with Path(path).open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record.to_dict(), ensure_ascii=False) + "\n")


def read_gold_jsonl(path: str | Path) -> list[GoldEdge]:
    records: list[GoldEdge] = []
    with Path(path).open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                records.append(GoldEdge(**json.loads(line)))
    return records


def validate_benchmark_integrity(records: list[GoldEdge]) -> None:
    """Fail fast on benchmark ID duplication or PMID split leakage."""
    ids: set[str] = set()
    pmid_splits: dict[str, set[str]] = {}
    for record in records:
        if record.benchmark_id in ids:
            raise ValueError(f"duplicate benchmark_id: {record.benchmark_id}")
        ids.add(record.benchmark_id)
        pmid_splits.setdefault(record.pmid, set()).add(record.split)
    leaked = {pmid: splits for pmid, splits in pmid_splits.items() if len(splits) > 1}
    if leaked:
        detail = ", ".join(f"{pmid}={sorted(splits)}" for pmid, splits in sorted(leaked.items()))
        raise ValueError(f"PMID split leakage: {detail}")
