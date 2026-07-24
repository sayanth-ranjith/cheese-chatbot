from typing import Any

import httpx

from app.core.document_loader.document_loader import Document
from app.core.embedding_model.embedding_model import EmbeddingModel


class JinaEmbeddingModel(EmbeddingModel):
    _EMBEDDINGS_URL = "https://api.jina.ai/v1/embeddings"

    def __init__(
        self,
        *,
        api_key: str,
        model_name: str = "jina-embeddings-v3",
        timeout_seconds: float = 30.0,
    ) -> None:
        if not api_key.strip():
            raise ValueError("Jina API key must not be empty")

        self._model_name = model_name
        self._client = httpx.Client(
            timeout=timeout_seconds,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
        )

    def embed_documents(
        self,
        documents: list[Document],
    ) -> list[list[float]]:
        if not documents:
            return []

        contents = [document.content for document in documents]

        return self._embed(
            texts=contents,
            task="retrieval.passage",
        )

    def embed_query(self, query: str) -> list[float]:
        if not query.strip():
            raise ValueError("Query must not be empty")

        embeddings = self._embed(
            texts=[query],
            task="retrieval.query",
        )

        return embeddings[0]

    def _embed(
        self,
        *,
        texts: list[str],
        task: str,
    ) -> list[list[float]]:
        response = self._client.post(
            self._EMBEDDINGS_URL,
            json={
                "model": self._model_name,
                "input": texts,
                "task": task,
            },
        )

        response.raise_for_status()

        payload: dict[str, Any] = response.json()
        data = payload.get("data")

        if not isinstance(data, list):
            raise RuntimeError("Invalid response from Jina Embeddings API")

        ordered_items = sorted(
            data,
            key=lambda item: item["index"],
        )

        return [item["embedding"] for item in ordered_items]

    def close(self) -> None:
        self._client.close()