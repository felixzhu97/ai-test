"""Cache adapter - implements CachePort interface."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional

from domain.ports.cache import CachePort, CacheEntry


def _get_cache_manager():
    """Lazy import cache manager to avoid circular imports."""
    from src.persistence.cache_manager import CacheManager
    return CacheManager()


class CacheAdapter(CachePort):
    """Cache adapter implementing CachePort interface."""

    def __init__(self, cache_manager=None) -> None:
        self._cache_manager = cache_manager or _get_cache_manager()

    async def get(self, key: str) -> Any | None:
        """Get a value from cache."""
        value = self._cache_manager._backend.get(key)
        if value is not None:
            return CacheEntry(key=key, value=value)
        return None

    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
    ) -> bool:
        """Set a value in cache."""
        try:
            self._cache_manager._backend.set(
                key,
                value,
                ttl_seconds=ttl if ttl is not None else 3600,
            )
            return True
        except Exception:
            return False

    async def delete(self, key: str) -> bool:
        """Delete a value from cache."""
        try:
            self._cache_manager._backend.delete(key)
            return True
        except Exception:
            return False

    async def exists(self, key: str) -> bool:
        """Check if a key exists in cache."""
        return self._cache_manager._backend.get(key) is not None

    async def clear(self, pattern: Optional[str] = None) -> int:
        """Clear cache entries."""
        try:
            if pattern:
                count = 0
                if hasattr(self._cache_manager._backend, "_cache"):
                    keys = list(self._cache_manager._backend._cache.keys())
                    for key in keys:
                        if pattern in key:
                            self._cache_manager._backend.delete(key)
                            count += 1
                return count
            else:
                self._cache_manager._backend.clear()
                return 1
        except Exception:
            return 0

    async def get_stats(self) -> dict[str, Any]:
        """Get cache statistics."""
        return self._cache_manager.get_stats()
