from __future__ import annotations

from dataclasses import dataclass

from forestconnectome.ids import normalize_text


@dataclass(frozen=True, slots=True)
class RelationNormalization:
    canonical: str
    reverse: bool = False


_DIRECT = {
    "regulates": "REGULATES",
    "regulate": "REGULATES",
    "controls": "REGULATES",
    "control": "REGULATES",
    "activates": "REGULATES_POSITIVELY",
    "activate": "REGULATES_POSITIVELY",
    "upregulates": "REGULATES_POSITIVELY",
    "positively regulates": "REGULATES_POSITIVELY",
    "represses": "REGULATES_NEGATIVELY",
    "repress": "REGULATES_NEGATIVELY",
    "downregulates": "REGULATES_NEGATIVELY",
    "negatively regulates": "REGULATES_NEGATIVELY",
    "binds": "BINDS",
    "bind": "BINDS",
    "interacts with": "INTERACTS_WITH",
    "interact with": "INTERACTS_WITH",
    "is expressed in": "EXPRESSED_IN",
    "expressed in": "EXPRESSED_IN",
    "localizes to": "LOCALIZED_IN",
    "localized in": "LOCALIZED_IN",
    "is involved in": "INVOLVED_IN",
    "involved in": "INVOLVED_IN",
    "associated with": "ASSOCIATED_WITH",
    "encodes": "ENCODES",
    "produces": "PRODUCES",
    "causes": "CAUSES",
    "inhibits": "INHIBITS",
    "promotes": "PROMOTES",
}

_PASSIVE = {
    "is regulated by": "REGULATES",
    "regulated by": "REGULATES",
    "is activated by": "REGULATES_POSITIVELY",
    "activated by": "REGULATES_POSITIVELY",
    "is repressed by": "REGULATES_NEGATIVELY",
    "repressed by": "REGULATES_NEGATIVELY",
    "is inhibited by": "INHIBITS",
    "inhibited by": "INHIBITS",
}


def normalize_relation(value: str) -> RelationNormalization:
    relation = normalize_text(value).strip(" .;:")
    if relation in _PASSIVE:
        return RelationNormalization(_PASSIVE[relation], reverse=True)
    if relation in _DIRECT:
        return RelationNormalization(_DIRECT[relation])
    canonical = relation.upper().replace("-", "_").replace(" ", "_")
    return RelationNormalization(canonical or "RELATED_TO")
