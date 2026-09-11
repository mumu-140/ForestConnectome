# Ontology grounding

ForestConnectome grounds shared biological concepts to authoritative ontology identifiers before semantic clustering or LLM-based entity resolution.

## Priority

1. Species-specific gene IDs and curated aliases are resolved by gene reference tables.
2. GO is used for biological process, molecular function and cellular component concepts.
3. Plant Ontology (PO) is used for plant anatomy, organs, tissues and developmental stages.
4. ChEBI is used for chemicals, metabolites and small molecules.
5. Exact ontology labels and exact synonyms are accepted deterministically.
6. Ambiguous or unresolved terms remain unresolved and may proceed to semantic retrieval/LLM review; the LLM is not allowed to invent a canonical CURIE.

A grounded concept receives a stable `ontology:<CURIE>` entity ID. The source wording is retained as the entity label/provenance context, while `canonical_ontology_id`, `ontology_prefix`, and `grounding_method` record the normalization decision.

## Reproducible snapshots

`config/ontologies.yaml` points to official GO, PO and ChEBI release artifacts. Run:

```bash
forestconnectome fetch-ontologies --output-dir data/reference/ontologies
```

The downloader stores the artifacts and a manifest containing URL, SHA256, byte size and fetch timestamp. Benchmarks and production graph builds should pin one manifest rather than silently using a moving ontology release.

## GO taxon constraints

ForestConnectome consumes GO's computed taxon-constraint artifact instead of reimplementing GO graph-propagation rules. `only_in_taxon` and `never_in_taxon` constraints are evaluated against the target species' NCBI lineage.

An unresolved GO taxon-union/grouping is `unknown`, never `pass`. Therefore an unknown grouping cannot unlock automatic transfer. The target lineage can be obtained with `forestconnectome.reference.ncbi_taxonomy`.

Taxon constraints are a gate on ontology applicability. Passing them does not prove that the source-species function is conserved in the target species.
