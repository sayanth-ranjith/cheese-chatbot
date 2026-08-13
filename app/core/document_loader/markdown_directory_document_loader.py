from pathlib import Path

from app.core.document_loader.document_loader import Document, DocumentLoader
from app.core.document_loader.markdown_document_loader import MarkdownDocumentLoader


class MarkdownDirectoryDocumentLoader(DocumentLoader):

    _MARKDOWN_SUFFIXES = {".md", ".markdown"}

    def __init__(self, directory_path: Path) -> None:
        self._directory_path = directory_path

    def load(self) -> list[Document]:
        self._validate_directory()

        documents: list[Document] = []

        for file_path in sorted(self._directory_path.rglob("*")):
            if file_path.suffix.lower() not in self._MARKDOWN_SUFFIXES:
                continue

            documents.extend(MarkdownDocumentLoader(file_path=file_path).load())

        return documents

    def _validate_directory(self) -> None:
        if not self._directory_path.exists():
            raise FileNotFoundError(
                f"Knowledge base directory does not exist: {self._directory_path}"
            )

        if not self._directory_path.is_dir():
            raise ValueError(
                f"Expected a directory but received: {self._directory_path}"
            )
