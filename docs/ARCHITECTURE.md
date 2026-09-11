# Architecture

## Pipeline

```text
Literature sources
  -> document acquisition
  -> structured chunks
  -> LLM candidate extraction
  -> verbatim evidence validation
  -> assertion + study-role + polarity separation
  -> per-entity taxon grounding
  -> authoritative entity/ontology grounding
       - genes: TAIR / Phytozome aliases
       - process/function/component: GO
       - plant anatomy/development: PO
       - chemicals/metabolites: ChEBI
  -> embedding + LLM fallback resolution
  -> canonical relation resolution
  -> direct-evidence graph

Arabidopsis reference graph
  + Ensembl Plants Compara orthology
  + OrthoFinder v3 gene-tree + duplication evidence
  + MCScanX_h independent collinearity/synteny
  -> T1-T4 orthology evidence tier
  -> predicate-specific transferability gate
  -> GO computed taxon-constraint + term-specificity gate
  -> transferred prediction / review / hypothesis layer

Direct + transferred graph
  -> validator/auditor
  -> review decisions
  -> benchmark + calibration dataset
  -> prompt/rule/model improvement
```

## Separation of evidence

A Populus claim can never become `direct` merely because the Arabidopsis ortholog has direct evidence. Transferred claims are computational predictions and retain the source claim, source taxon, source evidence type, source PMID/evidence span, orthology mapping and transfer decision metadata.

## Entity identity

Gene-like entities use a composite identity:

`taxon_id + genome_build + canonical_gene_id`

Symbols and aliases are attributes, not primary identity keys. Shared concepts such as processes, tissues and chemicals remain species-neutral canonical concepts; their taxonomic applicability belongs in evidence/ontology constraints.

## Statement context

The graph keeps three orthogonal statement dimensions:

- `assertion_status`: observed / inferred / predicted / hypothesized
- `study_role`: current result / prior work / review statement / discussion interpretation / derived transfer
- `polarity`: affirmed / negated / uncertain

Source and target taxa are independent. `study_taxa` records organisms that supplied experimental or computational evidence.

## Transfer hierarchy

T1-T4 describes **orthology evidence only**. It no longer directly authorizes edge propagation.

- T1: strong one-to-one orthology; potentially eligible for automatic functional transfer.
- T2: one-to-many/many-to-one; duplication risk means review-only by default.
- T3: expanded/many-to-many; hypothesis-only.
- T4: no functional transfer.

A second predicate-specific gate decides whether a claim may be projected. Regulatory, interaction, expression and phenotype-like edges are never automatically transferred from orthology alone. See `docs/TRANSFER_POLICY.md`.

## Confidence

LLM `model_confidence_raw` is retained for diagnostics but is not a scientific probability. Only `calibrated_confidence`, learned on a held-out human-reviewed benchmark (initially via scikit-learn isotonic regression), may be interpreted probabilistically.

## Producer/Auditor feedback

Every extracted or transferred edge carries a stable `claim_id`. Auditor outcomes are append-only records containing decision, error class, corrected fields, reviewer/model provenance, and timestamp. Producer prompts/rules are versioned so changes can be evaluated against a fixed benchmark set.

## Comparative evidence fusion

The comparative layer is multi-provider by design. Ensembl and OrthoFinder provide independent orthology calls; MCScanX_h provides collinearity evidence. Agreement can strengthen an orthology mapping, while disagreement is resolved conservatively toward the more duplication-prone interpretation. MCScanX synteny does not itself imply functional conservation.

OrthoFinder pairwise orthologue output may be reused as MCScanX_h third-party homology candidates. This avoids redundant homolog discovery while keeping the actual collinearity call independent.

## Ontology applicability

GO/PO/ChEBI grounding happens before semantic fallback. GO computed taxon constraints are checked against the target NCBI lineage before an ontology-backed functional claim can become an automatic transfer candidate. Unknown taxon groupings remain unknown and therefore cannot unlock automatic transfer.

## Benchmark gate

Bulk target-species propagation is not enabled merely because the pipeline executes. Automatic-transfer precision is calibrated on a locked, human-reviewed benchmark containing both known conservation positives and divergence/rewiring negatives. PMID and, where feasible, orthogroup/family grouping are used to prevent train-test leakage.
