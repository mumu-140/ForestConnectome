from __future__ import annotations

import hashlib
import re
import unicodedata


def normalize_text(value: str) -> str:
    value = unicodedata.normalize("NFKC", value).strip().lower()
    value = re.sub(r"\s+", " ", value)
    return value


def _digest(*parts: object, length: int = 20) -> str:
    payload = "\x1f".join("" if p is None else str(p) for p in parts)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:length]


def make_entity_id(
    *,
    entity_type: str,
    label: str,
    taxon_id: int | None = None,
    genome_build: str | None = None,
    canonical_gene_id: str | None = None,
    canonical_ontology_id: str | None = None,
) -> str:
    entity_type_norm = normalize_text(entity_type).replace(" ", "_")
    if entity_type_norm in {"gene", "gene_identifier", "protein", "transcription_factor", "enzyme"}:
        stable_name = canonical_gene_id or normalize_text(label)
        return f"{entity_type_norm}:{taxon_id or 'unknown'}:{genome_build or 'unknown'}:{stable_name}"
    if canonical_ontology_id:
        return f"ontology:{canonical_ontology_id}"
    return f"entity:{taxon_id or 'global'}:{entity_type_norm}:{_digest(normalize_text(label))}"


def make_claim_id(
    *,
    subject_id: str,
    predicate: str,
    object_id: str,
    source_id: str,
    chunk_id: str | None,
    evidence_text: str | None,
) -> str:
    return "claim:" + _digest(
        subject_id,
        normalize_text(predicate),
        object_id,
        source_id,
        chunk_id,
        normalize_text(evidence_text or ""),
        length=24,
    )
