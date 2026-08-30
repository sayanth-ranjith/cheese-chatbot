import certifi
from pymongo import MongoClient

from app.core.vector_store.vector_store import VectorSearchResult, VectorStore
from app.schemas.KnowledgeBaseModels import IngestedChunk


class MongoDBVectorStore(VectorStore):

    def __init__(
        self,
        *,
        uri: str,
        db_name: str,
        collection_name: str,
        index_name: str = "kb_vector_index",
    ) -> None:
        # Some hosting platforms ship a system CA bundle that fails TLS
        # negotiation with Atlas (SSL: TLSV1_ALERT_INTERNAL_ERROR); pinning
        # certifi's bundle avoids relying on the host's CA store.
        self._client: MongoClient = MongoClient(uri, tlsCAFile=certifi.where())
        self._collection = self._client[db_name][collection_name]
        self._index_name = index_name

    def add_documents(
        self,
        chunks: list[IngestedChunk],
    ) -> list[str]:
        if not chunks:
            return []

        documents = [
            {
                "content": chunk.content,
                "metadata": chunk.metadata,
                "embedding": chunk.embedding,
            }
            for chunk in chunks
        ]

        result = self._collection.insert_many(documents)

        return [str(inserted_id) for inserted_id in result.inserted_ids]

    def similarity_search(
        self,
        query_embedding: list[float],
        top_k: int = 5,
    ) -> list[VectorSearchResult]:
        pipeline = [
            {
                "$vectorSearch": {
                    "index": self._index_name,
                    "path": "embedding",
                    "queryVector": query_embedding,
                    "numCandidates": max(top_k * 10, 50),
                    "limit": top_k,
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "content": 1,
                    "metadata": 1,
                    "score": {"$meta": "vectorSearchScore"},
                }
            },
        ]

        return [
            VectorSearchResult(
                content=doc["content"],
                metadata=doc.get("metadata", {}),
                score=doc["score"],
            )
            for doc in self._collection.aggregate(pipeline)
        ]

    def close(self) -> None:
        self._client.close()
