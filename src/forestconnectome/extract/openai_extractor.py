from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any

from forestconnectome.extract.prompts import SYSTEM_PROMPT, user_prompt
from forestconnectome.extract.schema import ExtractionResult
from forestconnectome.ingest.chunking import TextChunk


def _strictify_schema(node: Any) -> Any:
    """Make a Pydantic JSON schema compatible with strict Structured Outputs.

    OpenAI strict schemas require object properties to be explicit and non-object
    fallbacks to be represented in the schema. Nullable values remain nullable;
    keys are required so the model must emit null rather than silently omit them.
    """
    if isinstance(node, dict):
        node = {key: _strictify_schema(value) for key, value in node.items()}
        if node.get("type") == "object" or "properties" in node:
            node["additionalProperties"] = False
            properties = node.get("properties", {})
            if properties:
                node["required"] = list(properties)
        return node
    if isinstance(node, list):
        return [_strictify_schema(item) for item in node]
    return node


@dataclass(slots=True)
class OpenAIExtractor:
    model: str = "gpt-5.6-luna"
    api_key: str | None = None
    store: bool = False

    def _client(self):
        try:
            from openai import OpenAI
        except ImportError as exc:  # pragma: no cover - optional dependency
            raise RuntimeError("Install forestconnectome[llm] to use OpenAI extraction") from exc
        return OpenAI(api_key=self.api_key or os.environ.get("OPENAI_API_KEY"))

    @staticmethod
    def response_format() -> dict[str, Any]:
        schema = _strictify_schema(ExtractionResult.model_json_schema())
        return {
            "type": "json_schema",
            "name": "forestconnectome_extraction",
            "description": "Evidence-traceable plant knowledge-graph edges",
            "schema": schema,
            "strict": True,
        }

    def request_body(self, chunk: TextChunk) -> dict[str, Any]:
        return {
            "model": self.model,
            "instructions": SYSTEM_PROMPT,
            "input": user_prompt(chunk),
            "text": {"format": self.response_format()},
            "store": self.store,
        }

    def extract(self, chunk: TextChunk) -> ExtractionResult:
        response = self._client().responses.create(**self.request_body(chunk))
        return ExtractionResult.model_validate_json(response.output_text)

    def batch_line(self, chunk: TextChunk) -> dict[str, Any]:
        """Return one JSONL object for OpenAI Batch API /v1/responses."""
        return {
            "custom_id": chunk.chunk_id,
            "method": "POST",
            "url": "/v1/responses",
            "body": self.request_body(chunk),
        }

    def batch_line_json(self, chunk: TextChunk) -> str:
        return json.dumps(self.batch_line(chunk), ensure_ascii=False, separators=(",", ":"))
