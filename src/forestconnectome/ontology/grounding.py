from __future__ import annotations

from dataclasses import dataclass, replace
from pathlib import Path
from typing import Iterable, Literal

from forestconnectome.ids import make_entity_id, normalize_text
from forestconnectome.models import Entity

GroundingStatus = Literal["exact_label", "exact_synonym", "ambiguous", "unresolved"]


@dataclass(frozen=True, slots=True)
class OntologyTermRecord:
    term_id: str
    label: str
    synonyms: tuple[str, ...] = ()
    definition: str | None = None
    obsolete: bool = False


@dataclass(frozen=True, slots=True)
class GroundingResult:
    status: GroundingStatus
    query: str
    ontology_prefix: str
    term_id: str | None = None
    label: str | None = None
    definition: str | None = None
    matched_text: str | None = None
    candidates: tuple[str, ...] = ()

    @property
    def resolved(self) -> bool:
        return self.status in {"exact_label", "exact_synonym"} and self.term_id is not None


class OntologyIndex:
    """Exact label/synonym index backed by an official ontology artifact."""

    def __init__(self, ontology_prefix: str, records: Iterable[OntologyTermRecord]):
        self.ontology_prefix = ontology_prefix.upper()
        self.records: dict[str, OntologyTermRecord] = {}
        self._labels: dict[str, list[str]] = {}
        self._synonyms: dict[str, list[str]] = {}
        for record in records:
            if record.obsolete:
                continue
            self.records[record.term_id] = record
            self._labels.setdefault(normalize_text(record.label), []).append(record.term_id)
            for synonym in record.synonyms:
                self._synonyms.setdefault(normalize_text(synonym), []).append(record.term_id)

    @classmethod
    def from_obo(cls, path: str | Path, *, ontology_prefix: str) -> "OntologyIndex":
        """Load an OBO/OWL ontology using pronto rather than a custom parser."""
        try:
            import pronto
        except ImportError as exc:
            raise RuntimeError("Install forestconnectome[ontology] to load ontology artifacts") from exc

        ontology = pronto.Ontology(str(path))
        records: list[OntologyTermRecord] = []
        prefix = ontology_prefix.upper() + ":"
        for term in ontology.terms():
            term_id = str(term.id)
            if not term_id.startswith(prefix):
                continue
            synonyms = tuple(str(s.description) for s in term.synonyms)
            definition = str(term.definition) if term.definition is not None else None
            records.append(
                OntologyTermRecord(
                    term_id=term_id,
                    label=str(term.name or term_id),
                    synonyms=synonyms,
                    definition=definition,
                    obsolete=bool(getattr(term, "obsolete", False)),
                )
            )
        return cls(ontology_prefix, records)

    def ground(self, query: str) -> GroundingResult:
        key = normalize_text(query)
        label_ids = tuple(dict.fromkeys(self._labels.get(key, ())))
        synonym_ids = tuple(dict.fromkeys(self._synonyms.get(key, ())))
        if len(label_ids) == 1:
            record = self.records[label_ids[0]]
            return GroundingResult("exact_label", query, self.ontology_prefix, record.term_id, record.label, record.definition, query)
        if len(label_ids) > 1:
            return GroundingResult("ambiguous", query, self.ontology_prefix, candidates=label_ids)
        if len(synonym_ids) == 1:
            record = self.records[synonym_ids[0]]
            return GroundingResult("exact_synonym", query, self.ontology_prefix, record.term_id, record.label, record.definition, query)
        if len(synonym_ids) > 1:
            return GroundingResult("ambiguous", query, self.ontology_prefix, candidates=synonym_ids)
        return GroundingResult("unresolved", query, self.ontology_prefix)


def apply_grounding(entity: Entity, result: GroundingResult) -> Entity:
    if not result.resolved or result.term_id is None:
        return entity
    if entity.canonical_gene_id is not None:
        raise ValueError("gene-like entities must be grounded through gene identifier sources, not concept ontologies")
    return replace(
        entity,
        entity_id=make_entity_id(entity_type=entity.entity_type, label=result.label or entity.label, canonical_ontology_id=result.term_id),
        canonical_ontology_id=result.term_id,
        ontology_prefix=result.ontology_prefix,
        grounding_method=result.status,
        definition=result.definition or entity.definition,
        resolution_status="exact" if result.status == "exact_label" else "alias_resolved",
    )
