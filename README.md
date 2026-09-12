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
        -> GO / PO / ChEBI grounding
        -> embedding + LLM fallback for unresolved concepts
        -> active-direction relation normalization
        -> direct claim JSONL

Arabidopsis direct claims
        + Ensembl Plants Compara
        + OrthoFinder v3 gene-tree/duplication evidence
        + MCScanX_h collinearity evidence
        -> fused T1/T2/T3/T4 orthology tier
        -> GO taxon constraints
        -> predicate/taxon/specificity transfer gate
        -> Populus prediction / review / hypothesis layer
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
- `docs/TRANSFER_POLICY.md` — literature-driven orthology-vs-edge-transfer guardrails
- `docs/ONTOLOGY_GROUNDING.md` — GO/PO/ChEBI grounding and GO taxon constraints
- `docs/COMPARATIVE_EVIDENCE.md` — Ensembl + OrthoFinder + MCScanX evidence fusion
- `docs/BENCHMARK.md` — evidence-span benchmark protocol
- `docs/METHOD_SOURCES.md` — upstream method/data references
- `schema/` — entity, claim and transfer JSON schemas

## v0.4 data and evidence layer

Snapshot the official concept ontologies:

```bash
forestconnectome fetch-ontologies --output-dir data/reference/ontologies
```

Convert OrthoFinder pairwise orthologues for MCScanX_h and import collinearity evidence:

```bash
forestconnectome build-mcscanx-homology orthologues.tsv arabidopsis_populus.homology
forestconnectome import-mcscanx arabidopsis_populus.collinearity synteny.jsonl
```

The first real benchmark seeds live in `data/benchmark/seed_articles.tsv` and `data/benchmark/gold_seed.jsonl`. They deliberately contain both functional-conservation positives and duplicate/expression/regulatory divergence controls.

## License

ForestConnectome code and repository-authored documentation are released under the **MIT License**; see `LICENSE`.

Third-party software, ontologies, literature and reference data remain under their own licenses and terms. See `THIRD_PARTY_NOTICES.md`. Restricted or non-redistributable external artifacts should remain outside the repository and be tracked by release/commit, source URL, retrieval time and SHA256 in the production provenance manifests.

## Status

v0.4.1 adds an explicit MIT license and third-party licensing boundary to the v0.4 scientific/data pipeline. Large-scale propagation remains disabled until the benchmark is independently curated and transfer precision is calibrated.
