# app/core/knowledge_base_config.py

from functools import lru_cache
from typing import Annotated

from fastapi import Depends

from app.core.config import Settings, get_settings
from app.core.document_loader.document_loader import DocumentLoader
from app.core.document_loader.markdown_directory_document_loader import (
    MarkdownDirectoryDocumentLoader,
)
from app.core.document_splitter.CharacterDocumentSplitter import (
    CharacterDocumentSplitter,
)
from app.core.document_splitter.document_splitter import DocumentSplitter
from app.core.embedding_config import get_embedding_model
from app.core.embedding_model.embedding_model import EmbeddingModel
from app.core.service.ingestion_service import IngestionService


@lru_cache
def get_document_loader() -> DocumentLoader:
    settings: Settings = get_settings()

    return MarkdownDirectoryDocumentLoader(
        directory_path=settings.knowledge_base_dir,
    )


@lru_cache
def get_document_splitter() -> DocumentSplitter:
    settings: Settings = get_settings()

    return CharacterDocumentSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
    )


def get_ingestion_service(
    loader: Annotated[DocumentLoader, Depends(get_document_loader)],
    splitter: Annotated[DocumentSplitter, Depends(get_document_splitter)],
    embedding_model: Annotated[EmbeddingModel, Depends(get_embedding_model)],
) -> IngestionService:
    return IngestionService(
        loader=loader,
        splitter=splitter,
        embedding_model=embedding_model,
    )


IngestionServiceDependency = Annotated[
    IngestionService,
    Depends(get_ingestion_service),
]
