from typing import Any

from pydantic import BaseModel


class IngestedChunk(BaseModel):
    content: str
    metadata: dict[str, Any]
    embedding: list[float]


class IngestResponse(BaseModel):
    documents_loaded: int
    chunks_created: int
    model: str
    chunks: list[IngestedChunk]
