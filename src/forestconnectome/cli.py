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
    return parser


def main() -> int:
    args = build_parser().parse_args()
    return args.func(args)
