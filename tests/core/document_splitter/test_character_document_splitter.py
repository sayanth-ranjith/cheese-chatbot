import pytest

from app.core.document_loader.document_loader import Document
from app.core.document_splitter.CharacterDocumentSplitter import (
    CharacterDocumentSplitter,
)


class TestInit:
    def test_defaults(self):
        splitter = CharacterDocumentSplitter()

        assert splitter._chunk_size == 1000
        assert splitter._chunk_overlap == 200

    def test_accepts_custom_values(self):
        splitter = CharacterDocumentSplitter(chunk_size=10, chunk_overlap=2)

        assert splitter._chunk_size == 10
        assert splitter._chunk_overlap == 2

    def test_rejects_zero_chunk_size(self):
        with pytest.raises(ValueError, match="chunk_size must be greater than zero"):
            CharacterDocumentSplitter(chunk_size=0, chunk_overlap=0)

    def test_rejects_negative_chunk_size(self):
        with pytest.raises(ValueError, match="chunk_size must be greater than zero"):
            CharacterDocumentSplitter(chunk_size=-5, chunk_overlap=0)

    def test_rejects_negative_chunk_overlap(self):
        with pytest.raises(ValueError, match="chunk_overlap cannot be negative"):
            CharacterDocumentSplitter(chunk_size=10, chunk_overlap=-1)

    def test_rejects_overlap_equal_to_chunk_size(self):
        with pytest.raises(
            ValueError, match="chunk_overlap must be smaller than chunk_size"
        ):
            CharacterDocumentSplitter(chunk_size=10, chunk_overlap=10)

    def test_rejects_overlap_greater_than_chunk_size(self):
        with pytest.raises(
            ValueError, match="chunk_overlap must be smaller than chunk_size"
        ):
            CharacterDocumentSplitter(chunk_size=10, chunk_overlap=20)


class TestSplit:
    def test_empty_document_list_returns_empty_list(self):
        splitter = CharacterDocumentSplitter()

        assert splitter.split([]) == []

    def test_empty_content_produces_no_chunks(self):
        splitter = CharacterDocumentSplitter()
        document = Document(content="   ", metadata={})

        assert splitter.split([document]) == []

    def test_content_shorter_than_chunk_size_produces_single_chunk(self):
        splitter = CharacterDocumentSplitter(chunk_size=1000, chunk_overlap=200)
        document = Document(content="hello world", metadata={"source": "a.txt"})

        chunks = splitter.split([document])

        assert len(chunks) == 1
        assert chunks[0].content == "hello world"
        assert chunks[0].metadata["source"] == "a.txt"
        assert chunks[0].metadata["chunk_index"] == 0
        assert chunks[0].metadata["chunk_start"] == 0
        assert chunks[0].metadata["chunk_end"] == 11

    def test_content_exactly_chunk_size_produces_single_chunk(self):
        splitter = CharacterDocumentSplitter(chunk_size=10, chunk_overlap=2)
        document = Document(content="a" * 10, metadata={})

        chunks = splitter.split([document])

        assert len(chunks) == 1
        assert chunks[0].content == "a" * 10

    def test_splits_long_content_into_overlapping_chunks(self):
        # 26 chars, chunk_size=10, overlap=2 -> step of 8 per chunk
        content = "abcdefghijklmnopqrstuvwxyz"
        splitter = CharacterDocumentSplitter(chunk_size=10, chunk_overlap=2)
        document = Document(content=content, metadata={})

        chunks = splitter.split([document])

        assert [c.content for c in chunks] == [
            "abcdefghij",  # 0-10
            "ijklmnopqr",  # 8-18
            "qrstuvwxyz",  # 16-26
        ]
        assert [c.metadata["chunk_index"] for c in chunks] == [0, 1, 2]
        assert [c.metadata["chunk_start"] for c in chunks] == [0, 8, 16]
        assert [c.metadata["chunk_end"] for c in chunks] == [10, 18, 26]

    def test_zero_overlap_produces_adjacent_non_overlapping_chunks(self):
        content = "abcdefghij"  # 10 chars
        splitter = CharacterDocumentSplitter(chunk_size=5, chunk_overlap=0)
        document = Document(content=content, metadata={})

        chunks = splitter.split([document])

        assert [c.content for c in chunks] == ["abcde", "fghij"]

    def test_strips_whitespace_from_chunk_content(self):
        splitter = CharacterDocumentSplitter(chunk_size=6, chunk_overlap=1)
        document = Document(content="  ab  cd  ", metadata={})

        chunks = splitter.split([document])

        assert all(c.content == c.content.strip() for c in chunks)
        assert all(c.content != "" for c in chunks)

    def test_preserves_original_document_metadata(self):
        splitter = CharacterDocumentSplitter(chunk_size=5, chunk_overlap=1)
        document = Document(
            content="abcdefghij", metadata={"source": "file.txt", "page": 1}
        )

        chunks = splitter.split([document])

        for chunk in chunks:
            assert chunk.metadata["source"] == "file.txt"
            assert chunk.metadata["page"] == 1

    def test_multiple_documents_are_all_split_and_flattened(self):
        splitter = CharacterDocumentSplitter(chunk_size=5, chunk_overlap=1)
        documents = [
            Document(content="abcdefghij", metadata={"source": "a"}),
            Document(content="klmno", metadata={"source": "b"}),
        ]

        chunks = splitter.split(documents)

        sources = [c.metadata["source"] for c in chunks]
        assert sources.count("a") == 3
        assert sources.count("b") == 1

    def test_chunk_index_restarts_per_document(self):
        splitter = CharacterDocumentSplitter(chunk_size=5, chunk_overlap=1)
        documents = [
            Document(content="abcdefghij", metadata={"source": "a"}),
            Document(content="klmno", metadata={"source": "b"}),
        ]

        chunks = splitter.split(documents)

        a_indexes = [c.metadata["chunk_index"] for c in chunks if c.metadata["source"] == "a"]
        b_indexes = [c.metadata["chunk_index"] for c in chunks if c.metadata["source"] == "b"]

        assert a_indexes == [0, 1, 2]
        assert b_indexes == [0]
