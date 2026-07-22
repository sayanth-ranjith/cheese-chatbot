from abc import ABC, abstractmethod

from app.core.document_loader.document_loader import Document


class DocumentSplitter(ABC):

    @abstractmethod
    def split(self, documents: list[Document]) -> list[Document]:
        raise NotImplementedError