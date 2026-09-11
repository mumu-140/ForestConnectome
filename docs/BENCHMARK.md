# Benchmark protocol

The benchmark is evidence-span based. The unit of annotation is a single auditable claim linked to one article and one minimal supporting span, not an entire paper-level label.

## Seed corpus

`data/benchmark/seed_articles.tsv` contains manually selected Arabidopsis-Populus papers covering:

- experimentally supported functional conservation;
- Populus target-species regulatory evidence;
- retained-duplicate divergence;
- expression divergence between orthologs; and
- computationally inferred conserved/rewired regulation.

These papers are seeds, not a final benchmark and not training data by default.

## Gold record

Each `GoldEdge` records source PMID, evidence span, subject/predicate/object, endpoint taxa, assertion status, study role, polarity, evidence type, extraction decision, transfer-conservation label and expected transfer disposition.

## Annotation protocol

For the locked test set, two curators independently annotate each candidate edge. Disagreements are adjudicated and the adjudicated record becomes gold. Curators should see the original paragraph/section and article metadata, not only an LLM-generated candidate.

## Leakage controls

- No PMID may occur in more than one split.
- Closely related evidence spans from the same experiment stay in the same split.
- For transfer evaluation, orthogroups/gene families should be group-split when feasible so paralogs of the same family do not leak between training and test sets.
- Ontology, alias-table, extraction-model and transfer-policy versions are recorded for every benchmark run.

## Metrics

Report at least:

- extraction precision, recall and F1 at edge level;
- exact entity grounding accuracy and unresolved/ambiguous rate;
- endpoint taxon accuracy;
- assertion/study-role/polarity accuracy;
- transfer-disposition confusion matrix by predicate class and orthology tier;
- precision of automatic-transfer candidates (primary safety metric);
- Brier score and calibration error for `calibrated_confidence`;
- results stratified by direct vs prior-work evidence, gene family, duplication status and source section.

Automatic transfer should optimize precision before recall. Low-confidence or scientifically non-transferable edges remain review/hypothesis candidates rather than being forced into the target-species graph.
