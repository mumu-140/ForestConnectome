from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

_HEADER = re.compile(r"^##\s*Alignment\s+(?P<block>\d+):\s+score=(?P<score>\S+)\s+e_value=(?P<evalue>\S+)\s+N=(?P<n>\d+)\s+(?P<pair>\S+)\s+(?P<orientation>\S+)")
_PAIR = re.compile(r"^\s*\d+-\s*\d+:\s+(?P<a>\S+)\s+(?P<b>\S+)\s+(?P<score>\S+)")


@dataclass(frozen=True, slots=True)
class MCScanXSyntenyPair:
    gene_a: str
    gene_b: str
    block_id: str
    block_score: float | None = None
    block_evalue: str | None = None
    orientation: str | None = None
    pair_score: str | None = None

    def matches(self, gene_1: str, gene_2: str) -> bool:
        return {self.gene_a, self.gene_b} == {gene_1, gene_2}


def _float_or_none(value: str | None) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except ValueError:
        return None


def parse_collinearity(path: str | Path) -> list[MCScanXSyntenyPair]:
    current: dict[str, str] = {}
    records: list[MCScanXSyntenyPair] = []
    for raw in Path(path).read_text(encoding="utf-8").splitlines():
        header = _HEADER.match(raw)
        if header:
            current = header.groupdict()
            continue
        pair = _PAIR.match(raw)
        if pair and current:
            values = pair.groupdict()
            records.append(MCScanXSyntenyPair(values["a"], values["b"], current["block"], _float_or_none(current.get("score")), current.get("evalue"), current.get("orientation"), values.get("score")))
    return records


class MCScanXSyntenyIndex:
    def __init__(self, pairs: list[MCScanXSyntenyPair]):
        self._pairs: dict[frozenset[str], list[MCScanXSyntenyPair]] = {}
        for pair in pairs:
            self._pairs.setdefault(frozenset((pair.gene_a, pair.gene_b)), []).append(pair)

    def evidence_for(self, gene_a: str, gene_b: str) -> tuple[MCScanXSyntenyPair, ...]:
        return tuple(self._pairs.get(frozenset((gene_a, gene_b)), ()))

    def supports(self, gene_a: str, gene_b: str) -> bool:
        return bool(self.evidence_for(gene_a, gene_b))


def write_mcscanx_homology(orthologies, path: str | Path, *, default_score: float = 1.0) -> int:
    """Write OrthoFinder gene pairs as MCScanX_h third-party homology input."""
    output = Path(path)
    seen: set[tuple[str, str]] = set()
    count = 0
    with output.open("w", encoding="utf-8") as handle:
        for record in orthologies:
            pair = (record.source_gene, record.target_gene)
            reverse = (record.target_gene, record.source_gene)
            if pair in seen or reverse in seen:
                continue
            seen.add(pair)
            handle.write(f"{record.source_gene}\t{record.target_gene}\t{default_score:g}\n")
            count += 1
    return count
