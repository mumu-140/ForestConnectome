# ForestConnectome

Comparative plant knowledge graph for woody plants, using Arabidopsis as a reference-transfer layer and Populus trichocarpa as the first target species.

## Design principles

1. Direct experimental evidence and transferred knowledge are stored separately.
2. Every biological claim must retain PMID/DOI, evidence span/chunk, species scope, and assertion status.
3. Gene identity is taxon-aware and genome-version-aware.
4. Orthology transfer is explicit, confidence-scored, and never silently collapsed into direct evidence.
5. Arabidopsis is retained as a dense reference layer rather than replaced.
6. Entity/relation normalization follows the PlantConnectome pattern: embeddings -> clustering -> LLM judgement -> validation.

## Initial scope

- Reference species: Arabidopsis thaliana (NCBI Taxonomy 3702)
- First target: Populus trichocarpa (NCBI Taxonomy 3694)
- Future targets: Populus spp., Salix spp., Eucalyptus spp., Quercus spp., Pinus spp., Picea spp.

## Core layers

- `reference`: Arabidopsis literature-derived graph
- `direct`: species-specific experimental evidence
- `orthology`: ortholog/paralog/synteny links
- `transfer`: inferred edges projected from a reference species
- `audit`: automated and human validation decisions

See `docs/ARCHITECTURE.md` and `schema/`.
