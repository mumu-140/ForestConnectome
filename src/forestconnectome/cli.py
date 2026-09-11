from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

from forestconnectome.extract.openai_extractor import OpenAIExtractor
from forestconnectome.ingest.chunking import TextSection, chunk_document


def _chunk(args: argparse.Namespace) -> int:
    text = Path(args.input).read_text(encoding="utf-8")
    chunks = chunk_document(
        args.source_id,
        [TextSection(args.section, text)],
        max_chars=args.max_chars,
        overlap_chars=args.overlap_chars,
    )
    with Path(args.output).open("w", encoding="utf-8") as out:
        for chunk in chunks:
            out.write(json.dumps(asdict(chunk), ensure_ascii=False) + "\n")
    return 0


def _batch(args: argparse.Namespace) -> int:
    extractor = OpenAIExtractor(model=args.model)
    with Path(args.input).open("r", encoding="utf-8") as inp, Path(args.output).open("w", encoding="utf-8") as out:
        for line in inp:
            row = json.loads(line)
            from forestconnectome.ingest.chunking import TextChunk

            chunk = TextChunk(**row)
            out.write(extractor.batch_line_json(chunk) + "\n")
    return 0


def _fetch_ontologies(args: argparse.Namespace) -> int:
    from forestconnectome.ontology.artifacts import fetch_configured_ontologies

    snapshots = fetch_configured_ontologies(args.config, args.output_dir)
    print(json.dumps([asdict(item) for item in snapshots], indent=2))
    return 0


def _import_orthofinder(args: argparse.Namespace) -> int:
    from forestconnectome.reference.orthofinder import parse_orthologues_tsv

    records = parse_orthologues_tsv(args.input)
    with Path(args.output).open("w", encoding="utf-8") as out:
        for record in records:
            out.write(json.dumps(asdict(record), ensure_ascii=False) + "\n")
    return 0


def _import_orthofinder_duplications(args: argparse.Namespace) -> int:
    from forestconnectome.reference.orthofinder import parse_duplications_tsv

    records = parse_duplications_tsv(args.input)
    with Path(args.output).open("w", encoding="utf-8") as out:
        for record in records:
            out.write(json.dumps(asdict(record), ensure_ascii=False) + "\n")
    return 0


def _import_mcscanx(args: argparse.Namespace) -> int:
    from forestconnectome.reference.mcscanx import parse_collinearity

    records = parse_collinearity(args.input)
    with Path(args.output).open("w", encoding="utf-8") as out:
        for record in records:
            out.write(json.dumps(asdict(record), ensure_ascii=False) + "\n")
    return 0


def _build_mcscanx_homology(args: argparse.Namespace) -> int:
    from forestconnectome.reference.mcscanx import write_mcscanx_homology
    from forestconnectome.reference.orthofinder import parse_orthologues_tsv

    records = parse_orthologues_tsv(args.input)
    count = write_mcscanx_homology(records, args.output, default_score=args.score)
    print(json.dumps({"pairs_written": count, "output": args.output}))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="forestconnectome")
    sub = parser.add_subparsers(dest="command", required=True)

    p_chunk = sub.add_parser("chunk", help="Chunk one plain-text article section into evidence-preserving JSONL")
    p_chunk.add_argument("input")
    p_chunk.add_argument("output")
    p_chunk.add_argument("--source-id", required=True)
    p_chunk.add_argument("--section", default="abstract")
    p_chunk.add_argument("--max-chars", type=int, default=12_000)
    p_chunk.add_argument("--overlap-chars", type=int, default=800)
    p_chunk.set_defaults(func=_chunk)

    p_batch = sub.add_parser("build-openai-batch", help="Convert chunk JSONL to OpenAI Batch /v1/responses JSONL")
    p_batch.add_argument("input")
    p_batch.add_argument("output")
    p_batch.add_argument("--model", default="gpt-5.6-luna")
    p_batch.set_defaults(func=_batch)

    p_ont = sub.add_parser("fetch-ontologies", help="Snapshot configured GO/PO/ChEBI artifacts and record SHA256 hashes")
    p_ont.add_argument("--config", default="config/ontologies.yaml")
    p_ont.add_argument("--output-dir", default="data/reference/ontologies")
    p_ont.set_defaults(func=_fetch_ontologies)

    p_of = sub.add_parser("import-orthofinder", help="Convert an OrthoFinder pairwise Orthologues TSV to pair-level JSONL")
    p_of.add_argument("input")
    p_of.add_argument("output")
    p_of.set_defaults(func=_import_orthofinder)

    p_dup = sub.add_parser("import-orthofinder-duplications", help="Convert OrthoFinder Duplications.tsv to JSONL")
    p_dup.add_argument("input")
    p_dup.add_argument("output")
    p_dup.set_defaults(func=_import_orthofinder_duplications)

    p_mc = sub.add_parser("import-mcscanx", help="Convert MCScanX .collinearity output to pair-level JSONL")
    p_mc.add_argument("input")
    p_mc.add_argument("output")
    p_mc.set_defaults(func=_import_mcscanx)

    p_mch = sub.add_parser(
        "build-mcscanx-homology",
        help="Convert OrthoFinder pairwise orthologues to MCScanX_h third-party homology input",
    )
    p_mch.add_argument("input", help="OrthoFinder pairwise Orthologues TSV")
    p_mch.add_argument("output", help="MCScanX_h .homology output")
    p_mch.add_argument("--score", type=float, default=1.0)
    p_mch.set_defaults(func=_build_mcscanx_homology)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    return args.func(args)
