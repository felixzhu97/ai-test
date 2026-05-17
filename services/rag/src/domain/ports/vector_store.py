"""Vector store port - abstract interface for vector storage operations."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any


@dataclass(frozen=True)
class SearchResult:
    """Immutable search result from vector store."""
    
    id: str
    text: str
    score: float
    payload: dict[str, Any] = field(default_factory=dict)


class VectorStorePort(ABC):
    """
    Abstract interface for vector storage operations.
    
    This port defines the contract for storing and retrieving
    vector embeddings. Implementations can use Qdrant, Milvus,
    Pinecone, or any other vector database.
    """
    
    @abstractmethod
    async def search(
        self,
        query_vector: list[float],
        top_k: int = 5,
        filter_conditions: dict[str, Any] | None = None,
    ) -> list[SearchResult]:
        """
        Search for similar vectors.
        
        Args:
            query_vector: The query embedding vector.
            top_k: Maximum number of results to return.
            filter_conditions: Optional filtering conditions.
            
        Returns:
            List of search results ordered by relevance.
        """
        pass
    
    @abstractmethod
    async def upsert(
        self,
        vectors: list[list[float]],
        texts: list[str],
        payloads: list[dict[str, Any]],
        batch_size: int = 100,
    ) -> list[str]:
        """
        Batch insert or update vectors.
        
        Args:
            vectors: List of embedding vectors.
            texts: List of corresponding text content.
            payloads: List of metadata payloads.
            batch_size: Number of vectors per batch.
            
        Returns:
            List of generated document IDs.
        """
        pass
    
    @abstractmethod
    async def delete(self, doc_id: str) -> bool:
        """
        Delete all vectors associated with a document.
        
        Args:
            doc_id: The document identifier.
            
        Returns:
            True if deletion was successful.
        """
        pass
    
    @abstractmethod
    async def delete_by_filter(self, filter_conditions: dict[str, Any]) -> int:
        """
        Delete vectors matching filter conditions.
        
        Args:
            filter_conditions: Filtering conditions.
            
        Returns:
            Number of deleted vectors.
        """
        pass
    
    @abstractmethod
    async def collection_exists(self, collection_name: str) -> bool:
        """
        Check if a collection exists.
        
        Args:
            collection_name: Name of the collection.
            
        Returns:
            True if collection exists.
        """
        pass
    
    @abstractmethod
    async def create_collection(
        self,
        collection_name: str,
        vector_size: int,
        distance_metric: str = "Cosine",
    ) -> bool:
        """
        Create a new collection.
        
        Args:
            collection_name: Name for the collection.
            vector_size: Dimension of embedding vectors.
            distance_metric: Distance metric (Cosine, Euclidean, DotProduct).
            
        Returns:
            True if collection was created.
        """
        pass
