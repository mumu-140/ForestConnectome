from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class OrthoFinderOrthology:
    orthogroup_id: str
    source_gene: str
    target_gene: str
    orthology_type: str
    source_copy_count: int
    target_copy_count: int

    @property
    def duplication_risk(self) -> bool:
        return self.source_copy_count > 1 or self.target_copy_count > 1


def _split_genes(value: str) -> tuple[str, ...]:
    if not value.strip():
        return ()
    return tuple(part.strip() for part in value.split(",") if part.strip())


def _orthology_type(source_count: int, target_count: int) -> str:
    if source_count == 1 and target_count == 1:
        return "one_to_one"
    if source_count == 1 and target_count > 1:
        return "one_to_many"
    if source_count > 1 and target_count == 1:
        return "many_to_one"
    return "many_to_many"


def parse_orthologues_tsv(path: str | Path) -> list[OrthoFinderOrthology]:
    with Path(path).open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        if reader.fieldnames is None or len(reader.fieldnames) != 3:
            raise ValueError("expected OrthoFinder pairwise TSV with Orthogroup plus two species columns")
        if reader.fieldnames[0] != "Orthogroup":
            raise ValueError("first OrthoFinder pairwise column must be Orthogroup")
        source_col, target_col = reader.fieldnames[1], reader.fieldnames[2]
        records: list[OrthoFinderOrthology] = []
        for row in reader:
            source_genes = _split_genes(row.get(source_col, ""))
            target_genes = _split_genes(row.get(target_col, ""))
            if not source_genes or not target_genes:
                continue
            relation = _orthology_type(len(source_genes), len(target_genes))
            for source_gene in source_genes:
                for target_gene in target_genes:
                    records.append(OrthoFinderOrthology(row["Orthogroup"], source_gene, target_gene, relation, len(source_genes), len(target_genes)))
    return records


@dataclass(frozen=True, slots=True)
class OrthoFinderDuplication:
    orthogroup_id: str
    species_tree_node: str
    gene_tree_node: str
    support: float
    duplication_type: str
    genes_1: tuple[str, ...]
    genes_2: tuple[str, ...]


def parse_duplications_tsv(path: str | Path) -> list[OrthoFinderDuplication]:
    with Path(path).open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        required = {"Orthogroup", "Species Tree node", "Gene tree node", "Support", "Type", "Genes 1", "Genes 2"}
        if reader.fieldnames is None or not required.issubset(set(reader.fieldnames)):
            raise ValueError("unexpected OrthoFinder Duplications.tsv header")
        return [
            OrthoFinderDuplication(row["Orthogroup"], row["Species Tree node"], row["Gene tree node"], float(row["Support"]), row["Type"], _split_genes(row["Genes 1"]), _split_genes(row["Genes 2"]))
            for row in reader
        ]
