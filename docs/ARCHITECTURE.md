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
  -> embedding + LLM fallback resolution
  -> canonical relation resolution
  -> direct-evidence graph

Arabidopsis reference graph
  + Ensembl/OrthoFinder orthology
  + independent synteny
  -> T1-T4 orthology evidence tier
  -> predicate-specific transferability gate
  -> taxon-constraint + term-specificity gate
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
