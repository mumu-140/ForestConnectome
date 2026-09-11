# Reference data contracts

Large reference datasets are intentionally not committed here.

## Gene alias table

Expected TSV columns:

`taxon_id  species  genome_build  canonical_gene_id  symbol  aliases`

`aliases` is a `|`-separated list. The alias resolver is taxon-aware: the same symbol in Arabidopsis and Populus remains two distinct entities.

Example:

```tsv
taxon_id\tspecies\tgenome_build\tcanonical_gene_id\tsymbol\taliases
3702\tArabidopsis thaliana\tTAIR10\tAT5G12870\tMYB46\tMYB46
3694\tPopulus trichocarpa\tPhytozome_v4.1\tPotri.005G000000\tMYB46-like\tPtMYB46|PtrMYB46
```

The Populus line above is illustrative only; production tables must be generated from an authoritative current identifier source rather than copied from the example.
