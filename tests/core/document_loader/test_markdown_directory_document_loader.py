import pytest

from app.core.document_loader.markdown_directory_document_loader import (
    MarkdownDirectoryDocumentLoader,
)


class TestLoad:
    def test_loads_all_markdown_files_in_directory(self, tmp_path):
        (tmp_path / "a.md").write_text("Alpha content", encoding="utf-8")
        (tmp_path / "b.markdown").write_text("Beta content", encoding="utf-8")

        loader = MarkdownDirectoryDocumentLoader(directory_path=tmp_path)
        documents = loader.load()

        contents = sorted(document.content for document in documents)
        assert contents == ["Alpha content", "Beta content"]

    def test_skips_non_markdown_files(self, tmp_path):
        (tmp_path / "a.md").write_text("Alpha content", encoding="utf-8")
        (tmp_path / "notes.txt").write_text("Ignore me", encoding="utf-8")

        loader = MarkdownDirectoryDocumentLoader(directory_path=tmp_path)
        documents = loader.load()

        assert len(documents) == 1
        assert documents[0].content == "Alpha content"

    def test_empty_directory_returns_empty_list(self, tmp_path):
        loader = MarkdownDirectoryDocumentLoader(directory_path=tmp_path)

        assert loader.load() == []

    def test_sets_source_metadata_per_file(self, tmp_path):
        file_path = tmp_path / "a.md"
        file_path.write_text("Alpha content", encoding="utf-8")

        loader = MarkdownDirectoryDocumentLoader(directory_path=tmp_path)
        documents = loader.load()

        assert documents[0].metadata["source"] == str(file_path)
        assert documents[0].metadata["file_name"] == "a.md"

    def test_missing_directory_raises_file_not_found_error(self, tmp_path):
        missing_dir = tmp_path / "does-not-exist"
        loader = MarkdownDirectoryDocumentLoader(directory_path=missing_dir)

        with pytest.raises(FileNotFoundError):
            loader.load()

    def test_path_that_is_a_file_raises_value_error(self, tmp_path):
        file_path = tmp_path / "a.md"
        file_path.write_text("Alpha content", encoding="utf-8")

        loader = MarkdownDirectoryDocumentLoader(directory_path=file_path)

        with pytest.raises(ValueError, match="Expected a directory"):
            loader.load()
