from app.core.document_loader.document_loader import Document
from app.core.embedding_model.jina_embedding_model import JinaEmbeddingModel

embedding_model = JinaEmbeddingModel(
    api_key="your-api-key",
)

documents = [
    Document(
        content="Cheese Retry supports configurable retry policies.",
        metadata={"source": "README.md"},
    ),
    Document(
        content="Exponential backoff increases the delay after each failure.",
        metadata={"source": "README.md"},
    ),
]

document_vectors = embedding_model.embed_documents(documents)

query_vector = embedding_model.embed_query(
    "How does retry backoff work?"
)

print(len(document_vectors))
print(len(document_vectors[0]))
print(len(query_vector))

embedding_model.close()