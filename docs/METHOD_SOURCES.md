# Method and data sources

This file records the upstream resources that define ForestConnectome's v0.4 implementation choices. URLs are source documentation, not vendored dependencies.

## Knowledge-graph baseline

- PlantConnectome (The Plant Cell, 2025): https://doi.org/10.1093/plcell/koaf169
- PlantConnectome application/source repository: https://github.com/mutwil/PlantConnectome_2025version

## Ontologies

- Gene Ontology downloads: https://geneontology.org/docs/download-ontology/
- GO taxon constraints: https://geneontology.org/docs/taxon-constraints/
- GO current ontology imports/releases: https://current.geneontology.org/ontology/imports/
- Plant Ontology / Planteome releases: https://github.com/Planteome/plant-ontology
- ChEBI downloads: https://www.ebi.ac.uk/chebi/downloadsForward.do
- Pronto ontology parser: https://pronto.readthedocs.io/

## Comparative genomics

- Ensembl Plants Compara homology method: https://plants.ensembl.org/info/genome/compara/homology_method.html
- OrthoFinder: https://github.com/davidemms/OrthoFinder
- OrthoFinder result-file documentation: https://orthofinder.github.io/OrthoFinder/tutorials/guide-to-results/
- MCScanX: https://github.com/wyp1125/MCScanX

## Benchmark literature

The initial seed papers are listed in `data/benchmark/seed_articles.tsv`. They include PMID 19965968, 20427511, 22236040, 23922694, 26819184, 21649762, 18694447 and 21232107. These span functional conservation, direct Populus regulatory evidence, retained-duplicate divergence, expression divergence and computational network conservation/rewiring.
