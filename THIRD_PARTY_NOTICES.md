# Third-party software and data

ForestConnectome is licensed under the MIT License. That license applies to code and documentation authored for this repository; it does not relicense third-party software, databases, ontologies, literature content, or reference data.

The repository currently declares third-party Python dependencies through `pyproject.toml` and integrates with external resources/tools such as Biopython/NCBI, OpenAI, FAISS, scikit-learn, Pronto, Gene Ontology, Plant Ontology, ChEBI, Ensembl Plants, OrthoFinder and MCScanX. These components and data sources remain subject to their own licenses, terms of use, citation requirements and redistribution restrictions.

No third-party source tree is intentionally vendored into this repository. External executable archives and restricted reference-data bundles should be downloaded into local analysis/storage locations and must not be committed unless their governing terms explicitly permit redistribution.

For production provenance, record the exact release/commit, source URL, retrieval time, file size, SHA256 digest, license/terms snapshot and redistribution status for every external artifact before it enters an executable manifest.
