from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

from forestconnectome.models import Claim


def write_claims(path: str | Path, claims: Iterable[Claim]) -> None:
    with Path(path).open("w", encoding="utf-8") as handle:
        for claim in claims:
            handle.write(json.dumps(claim.to_dict(), ensure_ascii=False) + "\n")
