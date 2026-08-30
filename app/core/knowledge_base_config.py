# app/core/knowledge_base_config.py

from functools import lru_cache
from typing import Annotated

from fastapi import Depends

from app.core.config import Settings, get_settings
from app.core.document_loader.composite_document_loader import (
    CompositeDocumentLoader,
)
from app.core.document_loader.document_loader import DocumentLoader
from app.core.document_loader.html_directory_document_loader import (
    HtmlDirectoryDocumentLoader,
)
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
from app.core.vector_store.mongodb_vector_store import MongoDBVectorStore
from app.core.vector_store.vector_store import VectorStore


@lru_cache
def get_document_loader() -> DocumentLoader:
    settings: Settings = get_settings()

    return CompositeDocumentLoader(
        loaders=[
            MarkdownDirectoryDocumentLoader(
                directory_path=settings.knowledge_base_dir,
            ),
            HtmlDirectoryDocumentLoader(
                directory_path=settings.knowledge_base_dir,
            ),
        ]
    )


@lru_cache
def get_document_splitter() -> DocumentSplitter:
    settings: Settings = get_settings()

    return CharacterDocumentSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
    )


@lru_cache
def get_vector_store() -> VectorStore:
    settings: Settings = get_settings()

    return MongoDBVectorStore(
        uri=settings.mongodb_uri.get_secret_value(),
        db_name=settings.mongodb_db_name,
        collection_name=settings.mongodb_collection,
        index_name=settings.mongodb_vector_index,
    )


def get_ingestion_service(
    loader: Annotated[DocumentLoader, Depends(get_document_loader)],
    splitter: Annotated[DocumentSplitter, Depends(get_document_splitter)],
    embedding_model: Annotated[EmbeddingModel, Depends(get_embedding_model)],
    vector_store: Annotated[VectorStore, Depends(get_vector_store)],
) -> IngestionService:
    return IngestionService(
        loader=loader,
        splitter=splitter,
        embedding_model=embedding_model,
        vector_store=vector_store,
    )


IngestionServiceDependency = Annotated[
    IngestionService,
    Depends(get_ingestion_service),
]
