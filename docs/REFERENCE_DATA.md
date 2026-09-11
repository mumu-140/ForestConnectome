# Reference-data strategy

ForestConnectome separates **canonical biological identity** from **programmatic comparative-genomics access**.

## Arabidopsis thaliana

- Canonical literature-facing gene namespace: **TAIR10**.
- Ensembl Plants is used as a programmatic mirror/xref source and as the comparative-genomics backbone.
- Direct Arabidopsis literature claims remain direct evidence; transfer is a separate derived layer.

## Populus trichocarpa

- Canonical literature-facing gene namespace: **JGI/Phytozome v4.1 `Potri.*` genes**.
- Current assembly target: **Pop_tri_v4 / GCA_000002775.4**.
- Historical `POPTR_*` and named aliases are retained as aliases, not canonical identities.
- Ensembl Plants imports the JGI annotation and provides current gene-tree/homology infrastructure.

A Phytozome v4.1 gene record can expose the current `Potri.*` identifier together with older `POPTR_*` aliases and UniProt cross-references. This is exactly why alias reconciliation is a separate ingest step instead of an LLM decision.

## Orthology backbone

The first transfer backbone is **Ensembl Plants Compara** with `compara=plants`.

Ensembl gene trees infer one-to-one, one-to-many and many-to-many orthology/paralogy relationships by reconciling gene trees with the species tree. ForestConnectome preserves the raw Ensembl homology type and target stable ID rather than collapsing it directly into a functional claim.

Important guardrail: an Ensembl orthology call alone does **not** set `synteny_support=true`. T1 transfer requires an independent synteny signal. This prevents a convenient API response from being promoted to stronger evidence than it actually contains.

## Secondary forest resources

- **TreeGenes** is retained as a forest-genomics archive and literature/phenotype source. Its Populus page exposes multiple genome versions, but the surfaced summary/annotation downloads are not treated as the canonical v4.1 alias authority.
- **PlantGenIE** is useful for forest-specific expression/annotation enrichment and has a public API surface, but is not a hard dependency because the site currently warns about maintenance/partial availability.

## Data products to generate

1. `arabidopsis_gene_aliases.tsv` — TAIR10 IDs, symbols, aliases and current Ensembl xrefs.
2. `populus_trichocarpa_gene_aliases.tsv` — Phytozome v4.1 `Potri.*` IDs plus historical IDs/symbols/xrefs.
3. `arabidopsis_populus_homologies.jsonl` — raw Ensembl Compara homology records.
4. `arabidopsis_populus_transfer_candidates.jsonl` — normalized candidate mappings before T1-T4 scoring.
5. a manually reviewed benchmark subset used to calibrate transfer thresholds before bulk propagation.
