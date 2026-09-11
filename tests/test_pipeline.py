from forestconnectome.extract.schema import ExtractedEdge, ExtractionResult, TaxonContext
from forestconnectome.ingest.chunking import TextChunk
from forestconnectome.pipeline import process_chunk


class FakeExtractor:
    model = "fake"

    def extract(self, chunk):
        return ExtractionResult(edges=[
            ExtractedEdge(
                source="A",
                source_type="gene",
                source_species="Populus trichocarpa",
                source_taxon_id=3694,
                relationship="is activated by",
                target="B",
                target_type="gene",
                target_species="Populus trichocarpa",
                target_taxon_id=3694,
                study_taxa=[TaxonContext(species="Populus trichocarpa", taxon_id=3694, role="experimental")],
                species_scope="exact_species",
                assertion_status="observed",
                study_role="current_result",
                polarity="affirmed",
                evidence_type="genetic",
                relationship_basis="mutant analysis",
                evidence_text="B activates A.",
                source_definition=None,
                target_definition=None,
                model_confidence_raw=0.9,
            )
        ])


def test_process_chunk_reverses_passive_relation():
    chunk = TextChunk("PMID:1", "PMID:1:results:0000", "results", "B activates A.", 0, 14)
    processed = process_chunk(chunk, FakeExtractor(), pmid="1")
    assert len(processed.accepted_claims) == 1
    claim = processed.accepted_claims[0]
    assert claim.predicate == "REGULATES_POSITIVELY"
    assert claim.subject.label == "B"
    assert claim.object.label == "A"
    assert claim.model_confidence_raw == 0.9
    assert claim.calibrated_confidence is None
