"""FastAPI dependency injection container and dependency definitions."""

from __future__ import annotations

from functools import lru_cache
from typing import Annotated, Generator

from fastapi import Depends

from domain.ports import (
    VectorStorePort,
    EmbeddingPort,
    LLMGatewayPort,
    CachePort,
    DocumentRepositoryPort,
)
from infrastructure.adapters import (
    QdrantVectorStoreAdapter,
    SentenceTransformerEmbeddingAdapter,
    LangChainLLMGatewayAdapter,
    CacheAdapter,
    SQLiteDocumentRepositoryAdapter,
)


class ApplicationContainer:
    """Application service dependency injection container."""

    def __init__(self):
        self._vector_store: VectorStorePort | None = None
        self._embedding: EmbeddingPort | None = None
        self._llm: LLMGatewayPort | None = None
        self._cache: CachePort | None = None
        self._document_repository: DocumentRepositoryPort | None = None

    @property
    def vector_store(self) -> VectorStorePort:
        if self._vector_store is None:
            self._vector_store = QdrantVectorStoreAdapter()
        return self._vector_store

    @property
    def embedding(self) -> EmbeddingPort:
        if self._embedding is None:
            self._embedding = SentenceTransformerEmbeddingAdapter()
        return self._embedding

    @property
    def llm(self) -> LLMGatewayPort:
        if self._llm is None:
            self._llm = LangChainLLMGatewayAdapter()
        return self._llm

    @property
    def cache(self) -> CachePort:
        if self._cache is None:
            self._cache = CacheAdapter()
        return self._cache

    @property
    def document_repository(self) -> DocumentRepositoryPort:
        if self._document_repository is None:
            self._document_repository = SQLiteDocumentRepositoryAdapter()
        return self._document_repository

    def reset(self) -> None:
        """Reset all dependencies (for testing)."""
        self._vector_store = None
        self._embedding = None
        self._llm = None
        self._cache = None
        self._document_repository = None


_app_container: ApplicationContainer | None = None


def get_app_container() -> ApplicationContainer:
    """Get application container singleton."""
    global _app_container
    if _app_container is None:
        _app_container = ApplicationContainer()
    return _app_container


def reset_app_container() -> None:
    """Reset application container (for testing)."""
    global _app_container
    if _app_container is not None:
        _app_container.reset()
    _app_container = None


# ===== FastAPI dependency injection functions =====


def get_vector_store() -> VectorStorePort:
    """Vector store dependency injection."""
    return get_app_container().vector_store


def get_embedding() -> EmbeddingPort:
    """Embedding dependency injection."""
    return get_app_container().embedding


def get_llm() -> LLMGatewayPort:
    """LLM dependency injection."""
    return get_app_container().llm


def get_cache() -> CachePort:
    """Cache dependency injection."""
    return get_app_container().cache


def get_document_repository() -> DocumentRepositoryPort:
    """Document repository dependency injection."""
    return get_app_container().document_repository


# ===== Type aliases for FastAPI dependencies =====

VectorStoreDep = Annotated[VectorStorePort, Depends(get_vector_store)]
EmbeddingDep = Annotated[EmbeddingPort, Depends(get_embedding)]
LLMDep = Annotated[LLMGatewayPort, Depends(get_llm)]
CacheDep = Annotated[CachePort, Depends(get_cache)]
DocumentRepositoryDep = Annotated[DocumentRepositoryPort, Depends(get_document_repository)]
