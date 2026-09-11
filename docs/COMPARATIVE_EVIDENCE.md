# Comparative-genomics evidence

ForestConnectome deliberately separates orthology inference, duplication history and synteny. Agreement among methods strengthens a mapping but does not by itself prove conservation of a biological edge.

## Providers

### Ensembl Plants Compara

Used as the programmatic comparative-genomics backbone and one independent gene-tree orthology provider. Raw relationship type, identity values, taxonomy level and provider confidence are retained.

### OrthoFinder v3

Used to infer project-specific phylogenetic orthology, rooted gene-tree relationships, hierarchical orthogroups and duplication events. Pairwise `Orthologues` files and `Gene_Duplication_Events/Duplications.tsv` are imported explicitly.

One-to-many and many-to-many mappings are treated as duplication-risk evidence, not as interchangeable target genes.

### MCScanX_h

Used for independent collinearity/synteny support. ForestConnectome can convert OrthoFinder pairwise orthologues into the third-party homology format accepted by MCScanX_h:

```bash
forestconnectome build-mcscanx-homology \
  Orthologues/Arabidopsis_thaliana__v__Populus_trichocarpa.tsv \
  arabidopsis_populus.homology
```

The `.homology` and MCScanX GFF inputs must use the same canonical gene IDs. After MCScanX_h runs, import its pair-level evidence with:

```bash
forestconnectome import-mcscanx arabidopsis_populus.collinearity synteny.jsonl
```

Using OrthoFinder pairs as MCScanX_h homology candidates avoids a redundant second homology search. The independent evidence is the genomic collinearity detected by MCScanX, not the reused candidate-pair list.

## Evidence fusion

`ComparativeEvidenceBundle` combines Ensembl, OrthoFinder and MCScanX evidence per source-target gene pair. If Ensembl and OrthoFinder disagree on multiplicity, the more duplication-prone interpretation wins. T1 requires one-to-one orthology, independent synteny, and either explicit phylogenetic support or agreement between independent orthology methods.

Even T1 does not automatically transfer regulatory, interaction, expression or phenotype-like relationships. Claim transfer is evaluated separately by `transfer/policy.py`.
