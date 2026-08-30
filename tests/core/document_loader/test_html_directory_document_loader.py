import pytest

from app.core.document_loader.html_directory_document_loader import (
    HtmlDirectoryDocumentLoader,
)


class TestLoad:
    def test_loads_all_html_files_in_directory(self, tmp_path):
        (tmp_path / "a.html").write_text(
            "<main><p>Alpha</p></main>", encoding="utf-8"
        )
        (tmp_path / "b.htm").write_text(
            "<main><p>Beta</p></main>", encoding="utf-8"
        )

        loader = HtmlDirectoryDocumentLoader(directory_path=tmp_path)
        documents = loader.load()

        contents = sorted(document.content for document in documents)
        assert contents == ["Alpha", "Beta"]

    def test_skips_non_html_files(self, tmp_path):
        (tmp_path / "a.html").write_text(
            "<main><p>Alpha</p></main>", encoding="utf-8"
        )
        (tmp_path / "notes.txt").write_text("Ignore me", encoding="utf-8")

        loader = HtmlDirectoryDocumentLoader(directory_path=tmp_path)
        documents = loader.load()

        assert len(documents) == 1
        assert documents[0].content == "Alpha"

    def test_skips_known_javadoc_index_pages(self, tmp_path):
        (tmp_path / "index.html").write_text(
            "<main><p>Overview links</p></main>", encoding="utf-8"
        )
        (tmp_path / "RetryPolicy.html").write_text(
            "<main><p>Real class docs</p></main>", encoding="utf-8"
        )

        loader = HtmlDirectoryDocumentLoader(directory_path=tmp_path)
        documents = loader.load()

        assert len(documents) == 1
        assert documents[0].content == "Real class docs"

    def test_skips_class_use_and_legal_directories(self, tmp_path):
        class_use_dir = tmp_path / "class-use"
        class_use_dir.mkdir()
        (class_use_dir / "RetryPolicy.html").write_text(
            "<main><p>Usage links</p></main>", encoding="utf-8"
        )

        legal_dir = tmp_path / "legal"
        legal_dir.mkdir()
        (legal_dir / "jquery.html").write_text(
            "<main><p>License text</p></main>", encoding="utf-8"
        )

        (tmp_path / "RetryPolicy.html").write_text(
            "<main><p>Real class docs</p></main>", encoding="utf-8"
        )

        loader = HtmlDirectoryDocumentLoader(directory_path=tmp_path)
        documents = loader.load()

        assert len(documents) == 1
        assert documents[0].content == "Real class docs"

    def test_empty_directory_returns_empty_list(self, tmp_path):
        loader = HtmlDirectoryDocumentLoader(directory_path=tmp_path)

        assert loader.load() == []

    def test_missing_directory_raises_file_not_found_error(self, tmp_path):
        missing_dir = tmp_path / "does-not-exist"
        loader = HtmlDirectoryDocumentLoader(directory_path=missing_dir)

        with pytest.raises(FileNotFoundError):
            loader.load()

    def test_path_that_is_a_file_raises_value_error(self, tmp_path):
        file_path = tmp_path / "a.html"
        file_path.write_text("<main><p>Alpha</p></main>", encoding="utf-8")

        loader = HtmlDirectoryDocumentLoader(directory_path=file_path)

        with pytest.raises(ValueError, match="Expected a directory"):
            loader.load()
