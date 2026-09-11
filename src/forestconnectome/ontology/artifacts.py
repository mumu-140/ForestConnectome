from __future__ import annotations

import hashlib
import json
import shutil
import tempfile
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

import yaml


@dataclass(frozen=True, slots=True)
class ArtifactSnapshot:
    key: str
    url: str
    filename: str
    sha256: str
    size_bytes: int
    fetched_at: str


def sha256_file(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def download_artifact(key: str, url: str, destination: str | Path) -> ArtifactSnapshot:
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    request = Request(url, headers={"User-Agent": "ForestConnectome/0.4"})
    with tempfile.NamedTemporaryFile(dir=destination.parent, delete=False) as tmp:
        tmp_path = Path(tmp.name)
        with urlopen(request, timeout=120) as response:
            shutil.copyfileobj(response, tmp)
    tmp_path.replace(destination)
    return ArtifactSnapshot(key, url, destination.name, sha256_file(destination), destination.stat().st_size, datetime.now(timezone.utc).isoformat())


def fetch_configured_ontologies(config_path: str | Path, output_dir: str | Path) -> list[ArtifactSnapshot]:
    config = yaml.safe_load(Path(config_path).read_text(encoding="utf-8"))
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    targets: list[tuple[str, str, str]] = []
    for prefix, spec in config.get("ontologies", {}).items():
        targets.append((prefix, spec["source_url"], spec["artifact"]))
    taxon = config.get("go_taxon_constraints", {})
    if taxon:
        targets.append(("GO_TAXON_CONSTRAINTS", taxon["source_url"], taxon["artifact"]))
        targets.append(("GO_TAXON_GROUPINGS", taxon["grouping_source_url"], taxon["grouping_artifact"]))
    snapshots = [download_artifact(key, url, output_dir / filename) for key, url, filename in targets]
    manifest = {"generated_at": datetime.now(timezone.utc).isoformat(), "artifacts": [asdict(snapshot) for snapshot in snapshots]}
    (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return snapshots
