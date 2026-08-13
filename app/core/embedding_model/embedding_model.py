from abc import ABC, abstractmethod

from app.core.document_loader.document_loader import Document


class EmbeddingModel(ABC):

    @property
    @abstractmethod
    def model_name(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def embed_documents(
        self,
        documents: list[Document],
    ) -> list[list[float]]:
        raise NotImplementedError

    @abstractmethod
    def embed_query(
        self,
        query: str,
    ) -> list[float]:
        raise NotImplementedError