from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from app.schemas.KnowledgeBaseModels import IngestedChunk


@dataclass(frozen=True)
class VectorSearchResult:
    content: str
    metadata: dict[str, Any] = field(default_factory=dict)
    score: float = 0.0


class VectorStore(ABC):

    @abstractmethod
    def add_documents(
        self,
        chunks: list[IngestedChunk],
    ) -> list[str]:
        raise NotImplementedError

    @abstractmethod
    def similarity_search(
        self,
        query_embedding: list[float],
        top_k: int = 5,
    ) -> list[VectorSearchResult]:
        raise NotImplementedError
