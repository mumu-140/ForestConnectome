# ForestConnectome

Comparative plant knowledge graph for woody plants, using **Arabidopsis thaliana** as a dense reference-transfer layer and **Populus trichocarpa** as the first target species.

ForestConnectome is not a species-renamed copy of PlantConnectome. It retains the published PlantConnectome extraction/resolution strategy while making species identity, evidence provenance and orthology transfer explicit.

## Core design

- **Direct evidence and transferred knowledge are separate.** A Populus prediction transferred from Arabidopsis can never masquerade as a Populus experiment.
- **Gene identity is taxon-aware and genome-version-aware.** Symbols and aliases are attributes, not cross-species identity keys.
- **Shared biological concepts remain shared.** Processes, tissues, phenotypes and chemicals are not duplicated merely because evidence came from different species.
- **Every claim is auditable.** PMID/DOI, section/chunk, verbatim evidence span, relationship basis, model and extractor version are retained.
- **Arabidopsis is a reference layer, not discarded data.** Orthology/synteny mappings project selected reference claims into woody-plant hypothesis layers.
- **Resolution follows the PlantConnectome method.** Embeddings -> iterative FAISS K-means -> LLM semantic resolution/validation -> canonical graph.

## Initial scope

- Reference: Arabidopsis thaliana (NCBI Taxonomy 3702)
- Primary target: Populus trichocarpa (NCBI Taxonomy 3694)
- Planned: Populus spp., Salix spp., Eucalyptus spp., Quercus spp., Pinus spp., Picea spp.

## Current runnable path

```text
PubMed species+gene queries
        -> section-aware chunks
        -> structured LLM extraction
        -> evidence pre-validation
        -> taxon-aware gene alias resolution
        -> active-direction relation normalization
        -> direct claim JSONL

Arabidopsis direct claims
        + orthology/synteny mappings
        -> T1/T2/T3/T4 transfer policy
        -> Populus predicted claim layer
```

The OpenAI extractor uses the Responses API with strict JSON-schema output and can emit Batch API JSONL for `/v1/responses`.

## Install

```bash
python -m pip install -e '.[dev]'
# Add literature, LLM and resolution dependencies when needed:
python -m pip install -e '.[all]'
```

## Minimal CLI

Chunk a plain-text article section:

```bash
forestconnectome chunk abstract.txt chunks.jsonl \
  --source-id PMID:12345678 --section abstract
```

Build a Batch API input file:

```bash
forestconnectome build-openai-batch chunks.jsonl extraction_batch.jsonl \
  --model gpt-5.6-luna
```

API keys are never stored in the repository. Use `OPENAI_API_KEY`, `NCBI_EMAIL` and optionally `NCBI_API_KEY`.

## Model profiles

`config/models.yaml` contains both a `plantconnectome_2025` reproduction profile and a `forestconnectome_current` production profile. Model IDs remain configurable because account availability and recommended models change over time.

## Documentation

- `docs/ARCHITECTURE.md` — layer boundaries and transfer policy
- `docs/PLANTCONNECTOME_PORT.md` — what is reproduced from PlantConnectome and what ForestConnectome changes
- `data/reference/README.md` — taxon-aware gene alias table contract
- `schema/` — entity, claim and transfer JSON schemas

## Status

v0.2 establishes the executable ingestion/extraction/resolution/transfer skeleton. The next milestone is real Arabidopsis and Populus identifier catalogs plus a curated benchmark corpus before large-scale literature processing.
