from pathlib import Path

from app.core.document_loader.document_loader import Document, DocumentLoader
from app.core.document_loader.html_document_loader import HtmlDocumentLoader


class HtmlDirectoryDocumentLoader(DocumentLoader):
    """Loads HTML documents from a directory, skipping generated Javadoc
    index/navigation pages that carry no useful content for retrieval."""

    _HTML_SUFFIXES = {".html", ".htm"}

    _EXCLUDED_FILE_NAMES = {
        "index.html",
        "allclasses-index.html",
        "allpackages-index.html",
        "overview-summary.html",
        "overview-tree.html",
        "help-doc.html",
        "search.html",
        "deprecated-list.html",
        "serialized-form.html",
        "constant-values.html",
        "index-all.html",
        "package-tree.html",
        "package-use.html",
    }

    _EXCLUDED_PATH_SEGMENTS = {"class-use", "legal"}

    def __init__(self, directory_path: Path) -> None:
        self._directory_path = directory_path

    def load(self) -> list[Document]:
        self._validate_directory()

        documents: list[Document] = []

        for file_path in sorted(self._directory_path.rglob("*")):
            if file_path.suffix.lower() not in self._HTML_SUFFIXES:
                continue

            if file_path.name in self._EXCLUDED_FILE_NAMES:
                continue

            if self._EXCLUDED_PATH_SEGMENTS & set(file_path.parts):
                continue

            documents.extend(HtmlDocumentLoader(file_path=file_path).load())

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
