from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class TextSection:
    name: str
    text: str


@dataclass(frozen=True, slots=True)
class TextChunk:
    source_id: str
    chunk_id: str
    section: str
    text: str
    start_char: int
    end_char: int


def chunk_section(
    source_id: str,
    section: TextSection,
    *,
    max_chars: int = 12_000,
    overlap_chars: int = 800,
) -> list[TextChunk]:
    """Create deterministic section-aware chunks while preserving source offsets."""
    if max_chars <= 0:
        raise ValueError("max_chars must be positive")
    if overlap_chars < 0 or overlap_chars >= max_chars:
        raise ValueError("overlap_chars must satisfy 0 <= overlap_chars < max_chars")

    text = section.text.strip()
    if not text:
        return []

    chunks: list[TextChunk] = []
    start = 0
    index = 0
    while start < len(text):
        hard_end = min(start + max_chars, len(text))
        end = hard_end
        if hard_end < len(text):
            # Prefer paragraph/sentence boundaries, but do not make tiny chunks.
            search_from = start + int(max_chars * 0.65)
            boundary = max(
                text.rfind("\n\n", search_from, hard_end),
                text.rfind(". ", search_from, hard_end),
                text.rfind("; ", search_from, hard_end),
            )
            if boundary > start:
                end = boundary + (2 if text[boundary:boundary + 2] in {". ", "; "} else 0)

        chunk_text = text[start:end].strip()
        if chunk_text:
            chunks.append(
                TextChunk(
                    source_id=source_id,
                    chunk_id=f"{source_id}:{section.name.lower()}:{index:04d}",
                    section=section.name.lower(),
                    text=chunk_text,
                    start_char=start,
                    end_char=end,
                )
            )
            index += 1

        if end >= len(text):
            break
        next_start = max(0, end - overlap_chars)
        if next_start <= start:
            next_start = end
        start = next_start

    return chunks


def chunk_document(
    source_id: str,
    sections: list[TextSection],
    *,
    max_chars: int = 12_000,
    overlap_chars: int = 800,
) -> list[TextChunk]:
    chunks: list[TextChunk] = []
    for section in sections:
        chunks.extend(
            chunk_section(
                source_id,
                section,
                max_chars=max_chars,
                overlap_chars=overlap_chars,
            )
        )
    return chunks
