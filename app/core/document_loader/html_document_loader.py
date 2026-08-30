from pathlib import Path

from bs4 import BeautifulSoup

from app.core.document_loader.document_loader import Document, DocumentLoader


class HtmlDocumentLoader(DocumentLoader):

    _HTML_SUFFIXES = {".html", ".htm"}
    _NOISE_TAGS = ("script", "style", "nav", "header", "footer")

    def __init__(self, file_path: Path) -> None:
        self._file_path = file_path

    def load(self) -> list[Document]:
        self._validate_file()

        html = self._file_path.read_text(encoding="utf-8")
        soup = BeautifulSoup(html, "html.parser")

        for tag in soup.find_all(self._NOISE_TAGS):
            tag.decompose()

        content_root = soup.find("main") or soup.body or soup
        content = content_root.get_text(separator="\n", strip=True)

        if not content:
            return []

        document = Document(
            content=content,
            metadata={
                "source": str(self._file_path),
                "file_name": self._file_path.name,
                "file_type": "html",
            },
        )

        return [document]

    def _validate_file(self) -> None:
        if not self._file_path.exists():
            raise FileNotFoundError(
                f"HTML file does not exist: {self._file_path}"
            )

        if not self._file_path.is_file():
            raise ValueError(
                f"Expected a file but received: {self._file_path}"
            )

        if self._file_path.suffix.lower() not in self._HTML_SUFFIXES:
            raise ValueError(
                f"Expected an HTML file but received: {self._file_path.suffix}"
            )
