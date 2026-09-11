from forestconnectome.reference.ensembl import EnsemblHomology
from forestconnectome.reference.evidence import ComparativeEvidenceBundle
from forestconnectome.reference.mcscanx import MCScanXSyntenyPair
from forestconnectome.reference.orthofinder import OrthoFinderOrthology
from forestconnectome.transfer.policy import classify_transfer


def _ensembl(kind="one_to_one"):
    return EnsemblHomology(
        source_id="AT1G01010",
        target_id="Potri.001G000100",
        source_species="arabidopsis_thaliana",
        target_species="populus_trichocarpa",
        raw_type="ortholog_one2one",
        orthology_type=kind,
        source_percent_identity=70.0,
        target_percent_identity=68.0,
    )


def _orthofinder(kind="one_to_one"):
    return OrthoFinderOrthology("OG1", "AT1G01010", "Potri.001G000100", kind, 1, 1)


def test_consensus_plus_synteny_can_make_transparent_t1_evidence():
    bundle = ComparativeEvidenceBundle(
        "AT1G01010",
        "Potri.001G000100",
        ensembl=_ensembl(),
        orthofinder=_orthofinder(),
        synteny=(MCScanXSyntenyPair("AT1G01010", "Potri.001G000100", "0"),),
    )
    evidence = bundle.to_orthology_evidence()
    assert evidence.independent_method_consensus is True
    assert evidence.synteny_support is True
    assert classify_transfer(evidence) == "T1"


def test_provider_disagreement_downgrades_instead_of_forcing_consensus():
    bundle = ComparativeEvidenceBundle(
        "AT1G01010",
        "Potri.001G000100",
        ensembl=_ensembl("one_to_one"),
        orthofinder=_orthofinder("one_to_many"),
        synteny=(MCScanXSyntenyPair("AT1G01010", "Potri.001G000100", "0"),),
    )
    evidence = bundle.to_orthology_evidence()
    assert evidence.independent_method_consensus is False
    assert evidence.orthology_type == "one_to_many"
    assert classify_transfer(evidence) == "T3"
