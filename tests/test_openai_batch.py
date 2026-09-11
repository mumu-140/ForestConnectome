from forestconnectome.extract.openai_extractor import OpenAIExtractor
from forestconnectome.ingest.chunking import TextChunk


def test_batch_line_targets_responses_endpoint():
    chunk = TextChunk("PMID:1", "PMID:1:abstract:0000", "abstract", "A regulates B.", 0, 14)
    line = OpenAIExtractor(model="test-model").batch_line(chunk)
    assert line["url"] == "/v1/responses"
    assert line["custom_id"] == chunk.chunk_id
    assert line["body"]["text"]["format"]["type"] == "json_schema"
