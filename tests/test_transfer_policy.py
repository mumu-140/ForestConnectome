from forestconnectome.transfer.policy import OrthologyEvidence, classify_transfer, allows_automatic_transfer


def test_t1_requires_one_to_one_and_strong_support():
    e = OrthologyEvidence("one_to_one", synteny_support=True, phylogenetic_support=0.9)
    assert classify_transfer(e) == "T1"
    assert allows_automatic_transfer("T1")


def test_similarity_only_is_not_auto_transfer():
    e = OrthologyEvidence("homology_only", sequence_support=0.99)
    assert classify_transfer(e) == "T4"
    assert not allows_automatic_transfer("T4")
