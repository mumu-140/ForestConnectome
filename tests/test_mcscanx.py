from forestconnectome.reference.mcscanx import MCScanXSyntenyIndex, parse_collinearity, write_mcscanx_homology
from forestconnectome.reference.orthofinder import OrthoFinderOrthology


def test_parse_mcscanx_collinearity_pairs(tmp_path):
    path = tmp_path / "at_pop.collinearity"
    path.write_text(
        "## Alignment 0: score=100.0 e_value=1e-20 N=2 at1&pt1 plus\n"
        "  0-  0: AT1G01010 Potri.001G000100 1e-40\n"
        "  0-  1: AT1G01020 Potri.001G000200 1e-30\n",
        encoding="utf-8",
    )
    pairs = parse_collinearity(path)
    assert len(pairs) == 2
    assert pairs[0].block_id == "0"
    assert pairs[0].orientation == "plus"
    index = MCScanXSyntenyIndex(pairs)
    assert index.supports("AT1G01010", "Potri.001G000100")
    assert index.supports("Potri.001G000100", "AT1G01010")


def test_write_mcscanx_homology_from_orthofinder(tmp_path):
    records = [
        OrthoFinderOrthology("OG1", "AT1G01010", "Potri.001G000100", "one_to_one", 1, 1),
        OrthoFinderOrthology("OG1", "AT1G01010", "Potri.001G000100", "one_to_one", 1, 1),
        OrthoFinderOrthology("OG2", "AT1G01020", "Potri.001G000200", "one_to_one", 1, 1),
    ]
    output = tmp_path / "at_pop.homology"
    count = write_mcscanx_homology(records, output, default_score=1.0)
    assert count == 2
    assert output.read_text(encoding="utf-8").splitlines() == [
        "AT1G01010\tPotri.001G000100\t1",
        "AT1G01020\tPotri.001G000200\t1",
    ]
