import json

from forestconnectome.ontology.artifacts import fetch_configured_ontologies, sha256_file


def test_fetch_configured_ontologies_writes_manifest_and_hashes(tmp_path):
    source = tmp_path / "source.obo"
    source.write_text("format-version: 1.2\nontology: test\n", encoding="utf-8")
    config = tmp_path / "ontologies.yaml"
    config.write_text(
        "ontologies:\n"
        "  GO:\n"
        "    artifact: go-basic.obo\n"
        f"    source_url: {source.as_uri()}\n",
        encoding="utf-8",
    )
    output = tmp_path / "snapshots"
    rows = fetch_configured_ontologies(config, output)
    assert len(rows) == 1
    assert rows[0].sha256 == sha256_file(output / "go-basic.obo")
    manifest = json.loads((output / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["artifacts"][0]["key"] == "GO"
