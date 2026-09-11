from forestconnectome.extract.schema import ExtractedEdge, ExtractionResult
from forestconnectome.ingest.chunking import TextChunk
from forestconnectome.pipeline import process_chunk


class FakeExtractor:
    model = "fake"

    def extract(self, chunk):
        return ExtractionResult(edges=[
            ExtractedEdge(
                source="A",
                source_type="gene",
                relationship="is activated by",
                target="B",
                target_type="gene",
                species="Populus trichocarpa",
                taxon_id=3694,
                species_scope="exact_species",
                assertion_status="observed",
                evidence_type="genetic",
                relationship_basis="mutant analysis",
                evidence_text="B activates A.",
                source_definition=None,
                target_definition=None,
                confidence=0.9,
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
