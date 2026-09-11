from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True, slots=True)
class PubMedQuerySpecies:
    scientific_name: str
    aliases: tuple[str, ...] = ()


def build_gene_query(species: PubMedQuerySpecies, query_term: str) -> str:
    """Build a species-aware PubMed query analogous to PlantConnectome's retrieval step."""
    names = (species.scientific_name, *species.aliases)
    species_terms = " OR ".join(f'"{name}"[Title/Abstract]' for name in names if name)
    escaped_term = query_term.replace('"', "")
    return f"({species_terms}) AND \"{escaped_term}\"[tw]"


def search_pubmed(
    species: PubMedQuerySpecies,
    query_terms: Iterable[str],
    *,
    email: str | None = None,
    api_key: str | None = None,
    retmax_per_term: int = 100_000,
) -> set[str]:
    """Search PubMed with Biopython Entrez; returns de-duplicated PMID strings."""
    try:
        from Bio import Entrez
    except ImportError as exc:  # pragma: no cover - optional dependency
        raise RuntimeError("Install forestconnectome[literature] to use PubMed ingestion") from exc

    resolved_email = email or os.environ.get("NCBI_EMAIL")
    if not resolved_email:
        raise ValueError("NCBI email is required via email= or NCBI_EMAIL")
    Entrez.email = resolved_email
    Entrez.api_key = api_key or os.environ.get("NCBI_API_KEY")

    pmids: set[str] = set()
    for term in query_terms:
        query = build_gene_query(species, term)
        with Entrez.esearch(db="pubmed", term=query, retmax=retmax_per_term) as handle:
            result = Entrez.read(handle)
        pmids.update(str(x) for x in result.get("IdList", []))
    return pmids
