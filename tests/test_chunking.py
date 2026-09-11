from forestconnectome.ingest.chunking import TextSection, chunk_section


def test_chunks_have_stable_ids_and_overlap():
    text = ("A sentence about poplar regulation. " * 80).strip()
    chunks = chunk_section("PMID:1", TextSection("results", text), max_chars=300, overlap_chars=40)
    assert len(chunks) > 1
    assert chunks[0].chunk_id == "PMID:1:results:0000"
    assert chunks[0].end_char > chunks[1].start_char


def test_empty_section_yields_no_chunks():
    assert chunk_section("x", TextSection("abstract", "   ")) == []
