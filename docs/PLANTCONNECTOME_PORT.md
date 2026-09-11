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

### 2. Orthology strength is separate from claim transferability

T1-T4 describes the orthology evidence only. A T1 ortholog does not imply conservation of every regulatory, expression, interaction or phenotype edge. A second predicate-specific transfer gate decides whether the source claim becomes an automatic candidate, review candidate, hypothesis, or is blocked.

### 3. Transfer is never direct experimental evidence

A transferred Populus edge carries `evidence_origin=orthology_transfer` and `evidence_type=computational`. Source experimental semantics remain attached to the Arabidopsis source claim and are copied only into transfer metadata for provenance. They are never relabeled as Populus experiments.

### 4. Gene resolution and taxon context are explicit

Gene identity is keyed by taxon + genome build + canonical identifier where possible. A symbol such as MYB46 is not sufficient to collapse nodes across species or duplicated Populus paralogs. Source and target entities have independent taxon fields, while `study_taxa` records taxa that actually supplied experiment/computation evidence.

### 5. Assertion, study role and polarity are separate axes

A prior-work sentence can still describe an observed fact; therefore `background` is no longer an assertion status. ForestConnectome records:

- `assertion_status`: observed / inferred / predicted / hypothesized;
- `study_role`: current result / prior work / review statement / discussion interpretation;
- `polarity`: affirmed / negated / uncertain.

Hypotheses, prior-work-only evidence and non-affirmed relations are routed to review rather than silently entering the accepted direct graph.

### 6. Model self-confidence is not scientific confidence

`model_confidence_raw` is stored only as a diagnostic signal. It is not used as a probability and is not used to authorize transfer. `calibrated_confidence` is reserved for post-hoc calibration against a held-out, human-reviewed benchmark; the baseline implementation uses scikit-learn isotonic regression.

### 7. Current API transport

The 2025 reproduction profile retains the model family described by the paper. The production profile uses the Responses API with strict JSON-schema outputs and can emit `/v1/responses` Batch API JSONL.

## Resolution compatibility

The core compatibility targets are:

- entity embedding payload includes name + type + definition, plus explicit taxon/gene ID;
- iterative FAISS K-means defaults to a maximum cluster size of 30;
- type resolution supports a frequency-preserving reference set and cosine-similarity candidates;
- relation normalization converts passive relations to active direction before graph insertion;
- authoritative ID/xref/ontology grounding should precede embedding+LLM fallback resolution.
