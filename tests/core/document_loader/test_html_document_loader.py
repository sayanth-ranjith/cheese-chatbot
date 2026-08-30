import pytest

from app.core.document_loader.html_document_loader import HtmlDocumentLoader


class TestLoad:
    def test_extracts_main_content_text(self, tmp_path):
        file_path = tmp_path / "a.html"
        file_path.write_text(
            "<html><body><nav>skip me</nav>"
            "<main><h1>Title</h1><p>Alpha content</p></main>"
            "</body></html>",
            encoding="utf-8",
        )

        loader = HtmlDocumentLoader(file_path=file_path)
        documents = loader.load()

        assert len(documents) == 1
        assert "Alpha content" in documents[0].content
        assert "skip me" not in documents[0].content

    def test_strips_script_and_style_tags(self, tmp_path):
        file_path = tmp_path / "a.html"
        file_path.write_text(
            "<html><body><main>"
            "<script>console.log('noise')</script>"
            "<style>.x { color: red }</style>"
            "<p>Real content</p>"
            "</main></body></html>",
            encoding="utf-8",
        )

        loader = HtmlDocumentLoader(file_path=file_path)
        documents = loader.load()

        assert documents[0].content == "Real content"

    def test_falls_back_to_body_when_no_main_tag(self, tmp_path):
        file_path = tmp_path / "a.html"
        file_path.write_text(
            "<html><body><p>Body content</p></body></html>",
            encoding="utf-8",
        )

        loader = HtmlDocumentLoader(file_path=file_path)
        documents = loader.load()

        assert documents[0].content == "Body content"

    def test_empty_content_returns_empty_list(self, tmp_path):
        file_path = tmp_path / "a.html"
        file_path.write_text(
            "<html><body><nav>only nav</nav></body></html>",
            encoding="utf-8",
        )

        loader = HtmlDocumentLoader(file_path=file_path)

        assert loader.load() == []

    def test_sets_source_metadata(self, tmp_path):
        file_path = tmp_path / "a.html"
        file_path.write_text(
            "<html><body><main><p>Alpha</p></main></body></html>",
            encoding="utf-8",
        )

        loader = HtmlDocumentLoader(file_path=file_path)
        documents = loader.load()

        assert documents[0].metadata["source"] == str(file_path)
        assert documents[0].metadata["file_name"] == "a.html"
        assert documents[0].metadata["file_type"] == "html"

    def test_missing_file_raises_file_not_found_error(self, tmp_path):
        missing_file = tmp_path / "missing.html"
        loader = HtmlDocumentLoader(file_path=missing_file)

        with pytest.raises(FileNotFoundError):
            loader.load()

    def test_non_html_suffix_raises_value_error(self, tmp_path):
        file_path = tmp_path / "a.md"
        file_path.write_text("content", encoding="utf-8")

        loader = HtmlDocumentLoader(file_path=file_path)

        with pytest.raises(ValueError, match="Expected an HTML file"):
            loader.load()
