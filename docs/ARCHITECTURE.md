# Architecture

## Pipeline

```text
Literature sources
  -> document acquisition
  -> structured chunks
  -> LLM extraction
  -> evidence-normalized claims
  -> taxon-aware entity resolution
  -> relation resolution
  -> direct-evidence graph

Arabidopsis reference graph
  + orthology/synteny mapping
  -> transfer engine
  -> transferred-evidence graph

Direct + transferred graph
  -> validator/auditor
  -> review decisions
  -> feedback dataset
  -> prompt/rule/model improvement
```

## Separation of evidence

A Populus claim can never become `direct` merely because the Arabidopsis ortholog has direct evidence. Transferred claims keep their source claim, source taxon, target taxon, orthology assertion, and transfer confidence.

## Entity identity

Gene entities use a composite identity:

`taxon_id + genome_build + canonical_gene_id`

Symbols and aliases are attributes, not primary identity keys.

## Transfer hierarchy

- T1: supported 1:1 ortholog + synteny; high-confidence automatic transfer candidate.
- T2: 1:many or many:1 orthology with strong phylogenetic/synteny support; transfer retained as predicted.
- T3: expanded gene families; candidate-only transfer unless additional evidence exists.
- T4: sequence similarity alone; no automatic functional transfer.

## Producer/Auditor feedback

Every extracted or transferred edge carries a stable `claim_id`. Auditor outcomes are append-only records containing decision, error class, corrected fields, reviewer/model provenance, and timestamp. Producer prompts/rules are versioned so changes can be evaluated against a fixed benchmark set.
