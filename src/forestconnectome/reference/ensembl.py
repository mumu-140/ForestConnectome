from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen

from forestconnectome.transfer.policy import OrthologyEvidence


_POPULUS_V41_GENE = re.compile(r"^(Potri\.\d{3}G\d{6})(?:\.v4\.1)?$")


def canonicalize_populus_v41_gene_id(stable_id: str) -> str:
    """Map Ensembl's imported JGI v4.1 stable-ID spelling to Phytozome's gene ID."""
    match = _POPULUS_V41_GENE.fullmatch(stable_id)
    return match.group(1) if match else stable_id


def normalize_ensembl_orthology_type(raw_type: str) -> str:
    value = raw_type.lower()
    if "one2one" in value:
        return "one_to_one"
    if "one2many" in value:
        return "one_to_many"
    if "many2many" in value:
        return "many_to_many"
    if "ortholog" in value:
        return "many_to_many"
    return "homology_only"


@dataclass(frozen=True, slots=True)
class EnsemblHomology:
    source_id: str
    target_id: str
    source_species: str | None
    target_species: str | None
    raw_type: str
    orthology_type: str
    taxonomy_level: str | None = None
    source_percent_identity: float | None = None
    target_percent_identity: float | None = None
    confidence: float | None = None

    @property
    def sequence_support(self) -> float:
        values = [
            value / 100.0
            for value in (self.source_percent_identity, self.target_percent_identity)
            if value is not None
        ]
        return min(values) if values else 0.0

    def conservative_transfer_evidence(self) -> OrthologyEvidence:
        """Convert to transfer evidence without inventing synteny or phylogenetic scores."""
        return OrthologyEvidence(
            orthology_type=self.orthology_type,
            synteny_support=False,
            phylogenetic_support=0.0,
            sequence_support=self.sequence_support,
            expression_support=0.0,
        )


def parse_homology_response(payload: dict[str, Any]) -> list[EnsemblHomology]:
    records: list[EnsemblHomology] = []
    for block in payload.get("data", []):
        query_id = str(block.get("id") or "")
        for item in block.get("homologies", []):
            source = item.get("source") or {}
            target = item.get("target") or {}
            source_id = str(source.get("id") or query_id)
            target_id = canonicalize_populus_v41_gene_id(str(target.get("id") or ""))
            raw_type = str(item.get("type") or "")
            records.append(
                EnsemblHomology(
                    source_id=source_id,
                    target_id=target_id,
                    source_species=source.get("species"),
                    target_species=target.get("species"),
                    raw_type=raw_type,
                    orthology_type=normalize_ensembl_orthology_type(raw_type),
                    taxonomy_level=item.get("taxonomy_level"),
                    source_percent_identity=_as_float(source.get("perc_id")),
                    target_percent_identity=_as_float(target.get("perc_id")),
                    confidence=_as_float(item.get("confidence")),
                )
            )
    return records


def _as_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


@dataclass(slots=True)
class EnsemblRestClient:
    base_url: str = "https://rest.ensembl.org"
    timeout: float = 60.0
    user_agent: str = "ForestConnectome/0.3"

    def _url(self, path: str, params: dict[str, Any] | None = None) -> str:
        url = self.base_url.rstrip("/") + "/" + path.lstrip("/")
        if params:
            clean = {key: value for key, value in params.items() if value is not None}
            url += "?" + urlencode(clean)
        return url

    def _get_json(self, path: str, params: dict[str, Any] | None = None) -> dict[str, Any] | list[Any]:
        request = Request(
            self._url(path, params),
            headers={"Accept": "application/json", "Content-Type": "application/json", "User-Agent": self.user_agent},
        )
        with urlopen(request, timeout=self.timeout) as response:  # noqa: S310 - fixed trusted endpoint by default
            return json.loads(response.read().decode("utf-8"))

    def genome_info(self, species: str) -> dict[str, Any]:
        payload = self._get_json(f"info/genomes/{quote(species, safe='')}")
        if not isinstance(payload, dict):
            raise ValueError("unexpected Ensembl genome response")
        return payload

    def xrefs(self, stable_id: str, *, all_levels: bool = False) -> list[dict[str, Any]]:
        payload = self._get_json(
            f"xrefs/id/{quote(stable_id, safe='')}",
            {"all_levels": 1 if all_levels else 0},
        )
        if not isinstance(payload, list):
            raise ValueError("unexpected Ensembl xref response")
        return [item for item in payload if isinstance(item, dict)]

    def homologies(
        self,
        *,
        species: str,
        gene_id: str,
        target_species: str,
        compara: str = "plants",
    ) -> list[EnsemblHomology]:
        payload = self._get_json(
            f"homology/id/{quote(species, safe='')}/{quote(gene_id, safe='')}",
            {
                "target_species": target_species,
                "type": "orthologues",
                "compara": compara,
                "sequence": "none",
            },
        )
        if not isinstance(payload, dict):
            raise ValueError("unexpected Ensembl homology response")
        return parse_homology_response(payload)
