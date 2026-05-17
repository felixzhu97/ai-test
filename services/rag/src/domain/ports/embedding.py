"""Embedding port - abstract interface for embedding generation."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass


class EmbeddingPort(ABC):
    """
    Abstract interface for generating text embeddings.
    
    This port defines the contract for converting text into
    dense vector representations. Implementations can use
    Sentence Transformers, OpenAI, or any embedding model.
    """
    
    @property
    @abstractmethod
    def embedding_dim(self) -> int:
        """
        Get the dimension of embedding vectors.
        
        Returns:
            The dimensionality of the embedding vectors.
        """
        pass
    
    @property
    @abstractmethod
    def model_name(self) -> str:
        """
        Get the name of the embedding model.
        
        Returns:
            The model identifier/name.
        """
        pass
    
    @abstractmethod
    def embed(self, texts: list[str]) -> list[list[float]]:
        """
        Generate embeddings for a batch of texts (synchronous).
        
        Args:
            texts: List of text strings to embed.
            
        Returns:
            List of embedding vectors.
        """
        pass
    
    @abstractmethod
    def embed_query(self, text: str) -> list[float]:
        """
        Generate embedding for a single query text (synchronous).
        
        Args:
            text: The query text to embed.
            
        Returns:
            The embedding vector.
        """
        pass
    
    @abstractmethod
    async def async_embed(self, texts: list[str]) -> list[list[float]]:
        """
        Generate embeddings for a batch of texts (asynchronous).
        
        Args:
            texts: List of text strings to embed.
            
        Returns:
            List of embedding vectors.
        """
        pass
    
    @abstractmethod
    async def async_embed_query(self, text: str) -> list[float]:
        """
        Generate embedding for a single query text (asynchronous).
        
        Args:
            text: The query text to embed.
            
        Returns:
            The embedding vector.
        """
        pass
