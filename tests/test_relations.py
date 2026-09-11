from forestconnectome.resolve.relations import normalize_relation


def test_passive_relation_reverses_direction():
    normalized = normalize_relation("is activated by")
    assert normalized.canonical == "REGULATES_POSITIVELY"
    assert normalized.reverse is True
