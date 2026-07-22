from pathlib import Path

from app.core.document_loader.document_loader import DocumentLoader, Document


class MarkdownDocumentLoader(DocumentLoader):

    def __init__(self, file_path: Path) -> None:
        self._file_path = file_path

    def load(self) -> list[Document]:
        self._validate_file()

        content = self._file_path.read_text(encoding="utf-8")

        if not content.strip():
            return []

        document = Document(
            content=content,
            metadata={
                "source": str(self._file_path),
                "file_name": self._file_path.name,
                "file_type": "markdown",
            },
        )

        return [document]

    def _validate_file(self) -> None:
        if not self._file_path.exists():
            raise FileNotFoundError(
                f"Markdown file does not exist: {self._file_path}"
            )

        if not self._file_path.is_file():
            raise ValueError(
                f"Expected a file but received: {self._file_path}"
            )

        if self._file_path.suffix.lower() not in {".md", ".markdown"}:
            raise ValueError(
                f"Expected a Markdown file but received: {self._file_path.suffix}"
            )