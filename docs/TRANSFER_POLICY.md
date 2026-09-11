# Scientific transfer policy

ForestConnectome separates two questions that must not be conflated:

1. **How strong is the orthology assignment?** (`T1`–`T4`)
2. **Is this particular biological claim transferable?** (`automatic_candidate`, `review_candidate`, `hypothesis_only`, `blocked`)

A strong one-to-one ortholog does not imply conservation of every regulatory, expression, interaction, phenotype, or stress-response edge.

## Orthology tiers

- **T1** — one-to-one orthology with independent synteny plus strong phylogenetic support.
- **T2** — one-to-many/many-to-one with strong phylogenetic support; duplication risk is explicit.
- **T3** — expanded/many-to-many families.
- **T4** — homology/sequence similarity insufficient for functional propagation.

Only T1 can ever reach `automatic_candidate`. T2 is never automatic.

## Predicate gate

Initial conservative policy:

- `INVOLVED_IN`, `HAS_MOLECULAR_FUNCTION`: may become automatic candidates only for T1, after taxon constraints pass and term specificity is broad/moderate.
- `REGULATES*`, `BINDS`, `INTERACTS_WITH`, `EXPRESSED_IN`, phenotype/effect predicates: never automatic from orthology alone. T1 produces at most a review candidate.
- T2 produces review candidates or hypotheses depending on predicate sensitivity.
- T3 is hypothesis-only.
- T4 is blocked.

Regulatory-edge conservation should later integrate target orthology, cis-element/motif conservation, expression/coexpression and direct binding/regulation evidence where available.

## Evidence semantics

Transferred target claims use:

- `evidence_origin = orthology_transfer`
- `evidence_type = computational`
- `assertion_status = predicted` (or `hypothesized` for T3-like hypotheses)
- `study_role = derived_transfer`

The Arabidopsis source claim's experimental evidence type, PMID, evidence span and confidence fields are preserved in transfer metadata. They are never relabeled as Populus experimental evidence.

## Taxon model

Extraction records taxon identity independently for source and target entities, plus a separate list of study/evidence taxa. This supports sentences that directly compare Arabidopsis and Populus without forcing both endpoints into one species.

## Confidence

`model_confidence_raw` is the LLM's self-assessment and is not treated as a probability. `calibrated_confidence` is reserved for post-hoc calibration on held-out human-labelled benchmark data. The baseline implementation uses scikit-learn `IsotonicRegression`; calibration parameters must be learned from benchmark data, not hand-chosen.
