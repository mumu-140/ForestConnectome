from __future__ import annotations

import csv
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from forestconnectome.ids import normalize_text


@dataclass(frozen=True, slots=True)
class GeneRecord:
    taxon_id: int
    canonical_gene_id: str
    species: str
    genome_build: str | None = None
    symbol: str | None = None
    aliases: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class AliasResolution:
    record: GeneRecord | None
    status: str
    candidates: tuple[GeneRecord, ...] = ()


class GeneAliasIndex:
    """Taxon-aware alias index. Aliases never resolve across taxa."""

    def __init__(self, records: Iterable[GeneRecord]):
        self._by_alias: dict[tuple[int, str], list[GeneRecord]] = defaultdict(list)
        self._by_id: dict[tuple[int, str], GeneRecord] = {}
        for record in records:
            self._by_id[(record.taxon_id, normalize_text(record.canonical_gene_id))] = record
            names = {record.canonical_gene_id, *(record.aliases or ())}
            if record.symbol:
                names.add(record.symbol)
            for name in names:
                if name:
                    self._by_alias[(record.taxon_id, normalize_text(name))].append(record)

    def resolve(self, label: str, taxon_id: int) -> AliasResolution:
        key = (taxon_id, normalize_text(label))
        if key in self._by_id:
            record = self._by_id[key]
            return AliasResolution(record, "exact", (record,))
        candidates = tuple(dict.fromkeys(self._by_alias.get(key, [])))
        if len(candidates) == 1:
            return AliasResolution(candidates[0], "alias_resolved", candidates)
        if len(candidates) > 1:
            return AliasResolution(None, "ambiguous", candidates)
        return AliasResolution(None, "unresolved", ())

    @classmethod
    def from_tsv(cls, path: str | Path) -> "GeneAliasIndex":
        records: list[GeneRecord] = []
        with Path(path).open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle, delimiter="\t")
            for row in reader:
                aliases = tuple(a.strip() for a in (row.get("aliases") or "").split("|") if a.strip())
                records.append(
                    GeneRecord(
                        taxon_id=int(row["taxon_id"]),
                        canonical_gene_id=row["canonical_gene_id"],
                        species=row["species"],
                        genome_build=row.get("genome_build") or None,
                        symbol=row.get("symbol") or None,
                        aliases=aliases,
                    )
                )
        return cls(records)
