from forestconnectome.extract.openai_extractor import OpenAIExtractor


def _walk(node):
    if isinstance(node, dict):
        yield node
        for value in node.values():
            yield from _walk(value)
    elif isinstance(node, list):
        for value in node:
            yield from _walk(value)


def test_structured_output_schema_marks_all_object_fields_required():
    schema = OpenAIExtractor.response_format()["schema"]
    for node in _walk(schema):
        if node.get("type") == "object" or "properties" in node:
            assert node.get("additionalProperties") is False
            props = node.get("properties", {})
            if props:
                assert set(node.get("required", [])) == set(props)
