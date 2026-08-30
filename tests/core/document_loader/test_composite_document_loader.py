from app.core.document_loader.composite_document_loader import (
    CompositeDocumentLoader,
)
from app.core.document_loader.document_loader import Document, DocumentLoader


class FakeDocumentLoader(DocumentLoader):
    def __init__(self, documents: list[Document]) -> None:
        self._documents = documents

    def load(self) -> list[Document]:
        return self._documents


class TestLoad:
    def test_concatenates_documents_from_all_loaders(self):
        loader = CompositeDocumentLoader(
            loaders=[
                FakeDocumentLoader([Document(content="a")]),
                FakeDocumentLoader([Document(content="b"), Document(content="c")]),
            ]
        )

        documents = loader.load()

        assert [document.content for document in documents] == ["a", "b", "c"]

    def test_no_loaders_returns_empty_list(self):
        loader = CompositeDocumentLoader(loaders=[])

        assert loader.load() == []
