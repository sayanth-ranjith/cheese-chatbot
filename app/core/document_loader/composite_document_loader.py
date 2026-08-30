from app.core.document_loader.document_loader import Document, DocumentLoader


class CompositeDocumentLoader(DocumentLoader):

    def __init__(self, loaders: list[DocumentLoader]) -> None:
        self._loaders = loaders

    def load(self) -> list[Document]:
        documents: list[Document] = []

        for loader in self._loaders:
            documents.extend(loader.load())

        return documents
