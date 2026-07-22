from app.core.document_loader.document_loader import Document
from app.core.document_splitter.document_splitter import DocumentSplitter

class CharacterDocumentSplitter(DocumentSplitter):

    def __init__(
        self,
        *,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
    ) -> None:
        if chunk_size <= 0:
            raise ValueError("chunk_size must be greater than zero")

        if chunk_overlap < 0:
            raise ValueError("chunk_overlap cannot be negative")

        if chunk_overlap >= chunk_size:
            raise ValueError("chunk_overlap must be smaller than chunk_size")

        self._chunk_size = chunk_size
        self._chunk_overlap = chunk_overlap

    def split(self, documents: list[Document]) -> list[Document]:
        chunks: list[Document] = []

        for document in documents:
            chunks.extend(self._split_document(document))

        return chunks

    def _split_document(self, document: Document) -> list[Document]:
        content = document.content

        if not content.strip():
            return []

        chunks: list[Document] = []
        start = 0
        chunk_index = 0

        while start < len(content):
            end = min(start + self._chunk_size, len(content))
            chunk_content = content[start:end].strip()

            if chunk_content:
                metadata = {
                    **document.metadata,
                    "chunk_index": chunk_index,
                    "chunk_start": start,
                    "chunk_end": end,
                }

                chunks.append(
                    Document(
                        content=chunk_content,
                        metadata=metadata,
                    )
                )

                chunk_index += 1

            if end == len(content):
                break

            start = end - self._chunk_overlap

        return chunks