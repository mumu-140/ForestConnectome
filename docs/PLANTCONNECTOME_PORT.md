# PlantConnectome -> ForestConnectome port

## Reused scientific method

ForestConnectome deliberately follows the published PlantConnectome sequence:

1. retrieve species/gene-focused literature;
2. extract entity-relationship-entity edges and entity types;
3. retain species and relationship basis;
4. attach entity definitions;
5. resolve entity types using embedding similarity plus an LLM judge;
6. resolve entities using embeddings, iterative K-means (cluster cap 30), LLM sub-clustering and validation;
7. resolve relationships using source/relationship/target type context;
8. preserve source text for edge validation.

The public PlantConnectome research implementation is treated as a methodological reference rather than vendored source. ForestConnectome uses clean implementations with configurable paths, no hard-coded API keys, no fixed 128-thread assumption, and explicit taxon identity.

## ForestConnectome changes

### 1. Arabidopsis is retained as a reference layer

Arabidopsis direct evidence is not replaced. It becomes a dense reference graph used by an explicit orthology/synteny transfer layer.

### 2. Transfer is never direct evidence

A transferred Populus edge carries `evidence_origin=orthology_transfer`, `source_claim_id`, source/target taxa, orthology type, transfer tier and confidence. The underlying PMID/evidence span remains the Arabidopsis source unless independent Populus evidence exists.

### 3. Gene resolution is taxon-aware

Gene identity is keyed by taxon + genome build + canonical identifier where possible. A symbol such as MYB46 is not sufficient to collapse nodes across species or duplicated Populus paralogs.

### 4. Hypothesis/background handling is first-class

PlantConnectome reported a characteristic false positive in which a scientific question/hypothesis became a factual edge. ForestConnectome therefore requires `assertion_status` and routes `hypothesized` and `background` edges to review rather than the direct high-confidence graph.

### 5. Current API transport

The 2025 reproduction profile retains the model family described by the paper. The production profile uses the Responses API with strict JSON-schema outputs and can emit `/v1/responses` Batch API JSONL.

## Resolution compatibility

The core compatibility targets are:

- entity embedding payload includes name + type + definition, plus explicit taxon/gene ID;
- iterative FAISS K-means defaults to a maximum cluster size of 30;
- type resolution supports a frequency-preserving reference set and cosine-similarity candidates;
- relation normalization converts passive relations to active direction before graph insertion.
