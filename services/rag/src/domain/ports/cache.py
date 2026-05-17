"""Cache port - abstract interface for caching operations."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    pass


@dataclass(frozen=True)
class CacheEntry:
    """
    Immutable cache entry.
    
    Attributes:
        key: Cache key.
        value: Cached value.
        ttl: Time-to-live in seconds.
    """
    
    key: str
    value: Any
    ttl: int | None = None


class CachePort(ABC):
    """
    Abstract interface for caching operations.
    
    This port defines the contract for temporary data storage.
    Implementations can use Redis, Memcached, or in-memory cache.
    """
    
    @abstractmethod
    async def get(self, key: str) -> Any | None:
        """
        Get a value from cache.
        
        Args:
            key: The cache key.
            
        Returns:
            The cached value, or None if not found.
        """
        pass
    
    @abstractmethod
    async def set(
        self,
        key: str,
        value: Any,
        ttl: int | None = None,
    ) -> bool:
        """
        Set a value in cache.
        
        Args:
            key: The cache key.
            value: The value to cache.
            ttl: Time-to-live in seconds.
            
        Returns:
            True if successful.
        """
        pass
    
    @abstractmethod
    async def delete(self, key: str) -> bool:
        """
        Delete a value from cache.
        
        Args:
            key: The cache key.
            
        Returns:
            True if key was deleted.
        """
        pass
    
    @abstractmethod
    async def exists(self, key: str) -> bool:
        """
        Check if a key exists in cache.
        
        Args:
            key: The cache key.
            
        Returns:
            True if key exists.
        """
        pass
    
    @abstractmethod
    async def clear(self, pattern: str | None = None) -> int:
        """
        Clear cache entries.
        
        Args:
            pattern: Optional glob pattern to match keys.
            
        Returns:
            Number of entries cleared.
        """
        pass
    
    @abstractmethod
    async def get_stats(self) -> dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache metrics (hits, misses, size, etc.).
        """
        pass
