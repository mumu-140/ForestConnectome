from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True, slots=True)
class OrthologyEvidence:
    orthology_type: str
    synteny_support: bool = False
    phylogenetic_support: float = 0.0
    sequence_support: float = 0.0
    expression_support: float = 0.0


TransferDisposition = Literal["automatic_candidate", "review_candidate", "hypothesis_only", "blocked"]
TaxonConstraintStatus = Literal["pass", "fail", "unknown"]
TermSpecificity = Literal["broad", "moderate", "specific", "unknown"]


@dataclass(frozen=True, slots=True)
class TransferDecision:
    orthology_tier: str
    disposition: TransferDisposition
    reason_codes: tuple[str, ...]


_NEVER_AUTO_PREDICATES = {
    "REGULATES",
    "REGULATES_POSITIVELY",
    "REGULATES_NEGATIVELY",
    "BINDS",
    "INTERACTS_WITH",
    "EXPRESSED_IN",
    "ASSOCIATED_WITH",
    "CAUSES",
    "PROMOTES",
    "INHIBITS",
}

_FUNCTIONAL_AUTO_CANDIDATES = {
    "INVOLVED_IN",
    "HAS_MOLECULAR_FUNCTION",
}


def classify_transfer(e: OrthologyEvidence) -> str:
    """Classify orthology evidence only; this does not authorize knowledge transfer."""
    if e.orthology_type == "one_to_one" and e.synteny_support and e.phylogenetic_support >= 0.8:
        return "T1"
    if e.orthology_type in {"one_to_many", "many_to_one"} and e.phylogenetic_support >= 0.8:
        return "T2"
    if e.orthology_type in {"many_to_many", "one_to_many", "many_to_one"}:
        return "T3"
    return "T4"


def evaluate_transfer(
    *,
    predicate: str,
    orthology_tier: str,
    source_assertion_status: str,
    source_study_role: str,
    source_evidence_type: str,
    source_polarity: str,
    taxon_constraint_status: TaxonConstraintStatus = "unknown",
    term_specificity: TermSpecificity = "unknown",
) -> TransferDecision:
    """Decide whether a claim is transferable after orthology classification.

    The policy intentionally separates orthology confidence from edge conservation.
    T1 means a strong orthology relationship, not that every source-species relation
    is conserved in the target species.
    """
    reasons: list[str] = []

    if source_polarity != "affirmed":
        return TransferDecision(orthology_tier, "blocked", ("source_not_affirmed",))
    if source_assertion_status == "hypothesized":
        return TransferDecision(orthology_tier, "blocked", ("source_hypothesized",))
    if source_assertion_status != "observed":
        reasons.append("source_not_observed")
    if source_study_role != "current_result":
        reasons.append("source_not_current_result")
    if source_evidence_type not in {"genetic", "biochemical", "phenotypic"}:
        reasons.append("source_evidence_not_auto_transfer_grade")
    if orthology_tier == "T4":
        return TransferDecision(orthology_tier, "blocked", ("orthology_insufficient",))
    if taxon_constraint_status == "fail":
        return TransferDecision(orthology_tier, "blocked", ("taxon_constraint_failed",))

    if orthology_tier == "T3":
        reasons.append("expanded_or_many_to_many")
        return TransferDecision(orthology_tier, "hypothesis_only", tuple(reasons))

    if orthology_tier == "T2":
        reasons.append("duplication_or_one_to_many")
        if predicate in _NEVER_AUTO_PREDICATES:
            reasons.append("predicate_requires_direct_conservation_evidence")
            return TransferDecision(orthology_tier, "hypothesis_only", tuple(reasons))
        return TransferDecision(orthology_tier, "review_candidate", tuple(reasons))

    if predicate in _NEVER_AUTO_PREDICATES:
        reasons.append("predicate_requires_direct_conservation_evidence")
        return TransferDecision(orthology_tier, "review_candidate", tuple(reasons))

    if predicate not in _FUNCTIONAL_AUTO_CANDIDATES:
        reasons.append("predicate_not_auto_allowlisted")
        return TransferDecision(orthology_tier, "review_candidate", tuple(reasons))

    if taxon_constraint_status != "pass":
        reasons.append("taxon_constraint_unverified")
    if term_specificity not in {"broad", "moderate"}:
        reasons.append("term_specificity_not_transfer_safe")
    if reasons:
        return TransferDecision(orthology_tier, "review_candidate", tuple(reasons))

    return TransferDecision(orthology_tier, "automatic_candidate", ())
