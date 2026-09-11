from dataclasses import dataclass

@dataclass(frozen=True, slots=True)
class OrthologyEvidence:
    orthology_type: str
    synteny_support: bool = False
    phylogenetic_support: float = 0.0
    sequence_support: float = 0.0
    expression_support: float = 0.0


def classify_transfer(e: OrthologyEvidence) -> str:
    """Conservative baseline policy; intended to be calibrated on benchmark data."""
    if e.orthology_type == "one_to_one" and e.synteny_support and e.phylogenetic_support >= 0.8:
        return "T1"
    if e.orthology_type in {"one_to_many", "many_to_one"} and e.phylogenetic_support >= 0.8:
        return "T2"
    if e.orthology_type in {"many_to_many", "one_to_many", "many_to_one"}:
        return "T3"
    return "T4"


def allows_automatic_transfer(tier: str) -> bool:
    return tier in {"T1", "T2"}
