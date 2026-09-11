from __future__ import annotations

from dataclasses import replace
from pathlib import Path
from typing import Mapping

from forestconnectome.models import Claim, Entity
from forestconnectome.ontology.grounding import GroundingResult, OntologyIndex, apply_grounding

_GENE_LIKE = {"gene", "gene identifier", "protein", "transcription factor", "enzyme"}

_DEFAULT_ROUTE: dict[str, tuple[str, ...]] = {
    "biological process": ("GO",), "biological_process": ("GO",), "molecular function": ("GO",),
    "molecular_function": ("GO",), "cellular component": ("GO",), "cellular_component": ("GO",),
    "process": ("GO",), "function": ("GO",), "compartment": ("GO",),
    "tissue": ("PO",), "organ": ("PO",), "plant organ": ("PO",), "plant tissue": ("PO",),
    "plant cell": ("PO",), "developmental stage": ("PO",),
    "chemical": ("CHEBI",), "metabolite": ("CHEBI",), "small molecule": ("CHEBI",),
}


class OntologyRegistry:
    def __init__(self, indexes: Mapping[str, OntologyIndex], *, route: Mapping[str, tuple[str, ...]] | None = None):
        self.indexes = {key.upper(): value for key, value in indexes.items()}
        self.route = dict(_DEFAULT_ROUTE)
        if route:
            self.route.update({key.strip().lower(): tuple(x.upper() for x in value) for key, value in route.items()})

    @classmethod
    def from_artifact_dir(cls, artifact_dir: str, *, prefixes: tuple[str, ...] = ("GO", "PO", "CHEBI")) -> "OntologyRegistry":
        artifact_dir_path = Path(artifact_dir)
        filenames = {"GO": "go-basic.obo", "PO": "po.obo", "CHEBI": "chebi.obo"}
        indexes = {prefix: OntologyIndex.from_obo(artifact_dir_path / filenames[prefix], ontology_prefix=prefix) for prefix in prefixes}
        return cls(indexes)

    def ground_entity(self, entity: Entity) -> tuple[Entity, GroundingResult | None]:
        if entity.entity_type.strip().lower() in _GENE_LIKE or entity.canonical_gene_id is not None:
            return entity, None
        prefixes = self.route.get(entity.entity_type.strip().lower(), ())
        ambiguous: GroundingResult | None = None
        for prefix in prefixes:
            index = self.indexes.get(prefix)
            if index is None:
                continue
            result = index.ground(entity.label)
            if result.resolved:
                return apply_grounding(entity, result), result
            if result.status == "ambiguous":
                ambiguous = result
        return entity, ambiguous

    def ground_claim(self, claim: Claim) -> Claim:
        subject, _ = self.ground_entity(claim.subject)
        obj, _ = self.ground_entity(claim.object)
        return replace(claim, subject=subject, object=obj)
