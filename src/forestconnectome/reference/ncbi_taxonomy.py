from __future__ import annotations

import os
from typing import Any


def lineage_ids_from_record(record: dict[str, Any]) -> set[int]:
    ids: set[int] = set()
    taxid = record.get("TaxId")
    if taxid is not None:
        ids.add(int(taxid))
    for item in record.get("LineageEx", []):
        if item.get("TaxId") is not None:
            ids.add(int(item["TaxId"]))
    return ids


def fetch_ncbi_lineage(taxon_id: int, *, email: str | None = None, api_key: str | None = None) -> set[int]:
    try:
        from Bio import Entrez
    except ImportError as exc:
        raise RuntimeError("Install forestconnectome[literature] for NCBI taxonomy access") from exc
    resolved_email = email or os.environ.get("NCBI_EMAIL")
    if not resolved_email:
        raise ValueError("NCBI email is required via email= or NCBI_EMAIL")
    Entrez.email = resolved_email
    Entrez.api_key = api_key or os.environ.get("NCBI_API_KEY")
    with Entrez.efetch(db="taxonomy", id=str(taxon_id), retmode="xml") as handle:
        records = Entrez.read(handle)
    if not records:
        raise ValueError(f"NCBI taxonomy returned no record for {taxon_id}")
    return lineage_ids_from_record(records[0])
