from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Literal, Mapping

TaxonConstraintRelation = Literal["only_in_taxon", "never_in_taxon"]
TaxonConstraintStatus = Literal["pass", "fail", "unknown"]
ONLY_IN_TAXON = "RO:0002160"
NEVER_IN_TAXON = "RO:0002161"


@dataclass(frozen=True, slots=True)
class TaxonConstraint:
    term_id: str
    relation: TaxonConstraintRelation
    taxon_curie: str


@dataclass(frozen=True, slots=True)
class TaxonConstraintDecision:
    status: TaxonConstraintStatus
    reason_codes: tuple[str, ...]
    matched_constraints: tuple[TaxonConstraint, ...] = ()


class GoTaxonConstraintIndex:
    def __init__(self, constraints: Iterable[TaxonConstraint]):
        by_term: dict[str, list[TaxonConstraint]] = {}
        for constraint in constraints:
            by_term.setdefault(constraint.term_id, []).append(constraint)
        self._by_term = {key: tuple(value) for key, value in by_term.items()}

    @classmethod
    def from_obo(cls, path: str | Path) -> "GoTaxonConstraintIndex":
        try:
            import pronto
            from pronto import ResourcePropertyValue
        except ImportError as exc:
            raise RuntimeError("Install forestconnectome[ontology] to load GO taxon constraints") from exc
        ontology = pronto.Ontology(str(path))
        constraints: list[TaxonConstraint] = []
        for term in ontology.terms():
            term_id = str(term.id)
            if not term_id.startswith("GO:"):
                continue
            for annotation in term.annotations:
                if not isinstance(annotation, ResourcePropertyValue):
                    continue
                if annotation.property == ONLY_IN_TAXON:
                    constraints.append(TaxonConstraint(term_id, "only_in_taxon", annotation.resource))
                elif annotation.property == NEVER_IN_TAXON:
                    constraints.append(TaxonConstraint(term_id, "never_in_taxon", annotation.resource))
        return cls(constraints)

    def constraints_for(self, term_id: str) -> tuple[TaxonConstraint, ...]:
        return self._by_term.get(term_id, ())

    def evaluate(self, term_id: str, *, taxon_id: int, lineage_taxon_ids: Iterable[int], grouping_members: Mapping[str, set[int]] | None = None) -> TaxonConstraintDecision:
        constraints = self.constraints_for(term_id)
        if not constraints:
            return TaxonConstraintDecision("pass", ("no_go_taxon_constraint",))
        lineage = {int(x) for x in lineage_taxon_ids}
        lineage.add(int(taxon_id))
        grouping_members = grouping_members or {}
        matched: list[TaxonConstraint] = []
        unknown_group = False

        def applies(curie: str) -> bool | None:
            if curie.startswith("NCBITaxon:"):
                try:
                    return int(curie.split(":", 1)[1]) in lineage
                except ValueError:
                    return None
            members = grouping_members.get(curie)
            if members is None:
                return None
            return bool(lineage.intersection(members))

        only_constraints = [c for c in constraints if c.relation == "only_in_taxon"]
        never_constraints = [c for c in constraints if c.relation == "never_in_taxon"]
        for constraint in never_constraints:
            state = applies(constraint.taxon_curie)
            if state is True:
                matched.append(constraint)
                return TaxonConstraintDecision("fail", ("go_never_in_taxon",), tuple(matched))
            if state is None:
                unknown_group = True
        for constraint in only_constraints:
            state = applies(constraint.taxon_curie)
            if state is True:
                matched.append(constraint)
            elif state is False:
                return TaxonConstraintDecision("fail", ("go_only_in_taxon_mismatch",), tuple(matched))
            else:
                unknown_group = True
        if unknown_group:
            return TaxonConstraintDecision("unknown", ("unresolved_go_taxon_grouping",), tuple(matched))
        return TaxonConstraintDecision("pass", ("go_taxon_constraint_satisfied",), tuple(matched))


def evaluate_claim_go_constraints(claim, index: GoTaxonConstraintIndex, *, target_taxon_id: int, lineage_taxon_ids: Iterable[int], grouping_members: Mapping[str, set[int]] | None = None) -> TaxonConstraintDecision:
    term_ids = [getattr(entity, "canonical_ontology_id", None) for entity in (claim.subject, claim.object)]
    term_ids = [term_id for term_id in term_ids if term_id and term_id.startswith("GO:")]
    if not term_ids:
        return TaxonConstraintDecision("unknown", ("no_grounded_go_term",))
    decisions = [index.evaluate(term_id, taxon_id=target_taxon_id, lineage_taxon_ids=lineage_taxon_ids, grouping_members=grouping_members) for term_id in term_ids]
    failed = [decision for decision in decisions if decision.status == "fail"]
    if failed:
        matched = tuple(c for decision in failed for c in decision.matched_constraints)
        reasons = tuple(dict.fromkeys(reason for decision in failed for reason in decision.reason_codes))
        return TaxonConstraintDecision("fail", reasons, matched)
    unknown = [decision for decision in decisions if decision.status == "unknown"]
    if unknown:
        reasons = tuple(dict.fromkeys(reason for decision in unknown for reason in decision.reason_codes))
        return TaxonConstraintDecision("unknown", reasons)
    matched = tuple(c for decision in decisions for c in decision.matched_constraints)
    return TaxonConstraintDecision("pass", ("all_go_taxon_constraints_satisfied",), matched)
