from __future__ import annotations

from dataclasses import dataclass

from forestconnectome.reference.ensembl import EnsemblHomology
from forestconnectome.reference.mcscanx import MCScanXSyntenyPair
from forestconnectome.reference.orthofinder import OrthoFinderOrthology
from forestconnectome.transfer.policy import OrthologyEvidence


@dataclass(frozen=True, slots=True)
class ComparativeEvidenceBundle:
    source_gene: str
    target_gene: str
    ensembl: EnsemblHomology | None = None
    orthofinder: OrthoFinderOrthology | None = None
    synteny: tuple[MCScanXSyntenyPair, ...] = ()

    @property
    def provider_consensus(self) -> bool:
        return self.ensembl is not None and self.orthofinder is not None and self.ensembl.orthology_type == self.orthofinder.orthology_type

    @property
    def orthology_type(self) -> str:
        types = [value for value in (self.ensembl.orthology_type if self.ensembl else None, self.orthofinder.orthology_type if self.orthofinder else None) if value is not None]
        if not types:
            return "homology_only"
        if len(set(types)) == 1:
            return types[0]
        rank = {"one_to_one": 0, "one_to_many": 1, "many_to_one": 1, "many_to_many": 2, "homology_only": 3}
        return max(types, key=lambda value: rank.get(value, 3))

    def to_orthology_evidence(self) -> OrthologyEvidence:
        return OrthologyEvidence(
            orthology_type=self.orthology_type,
            synteny_support=bool(self.synteny),
            phylogenetic_support=0.0,
            sequence_support=self.ensembl.sequence_support if self.ensembl else 0.0,
            expression_support=0.0,
            independent_method_consensus=self.provider_consensus,
        )
