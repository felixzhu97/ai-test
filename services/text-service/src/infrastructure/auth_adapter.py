"""Authentication adapter for Clean Architecture.

This module provides authentication as an infrastructure concern,
wrapping the shared auth module and exposing it as a proper dependency.
"""

import os
from typing import Optional, Set
from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader
from loguru import logger


API_KEY_NAME = os.getenv("API_KEY_HEADER_NAME", "X-API-Key")
_API_KEYS: Set[str] = set()


def _load_api_keys() -> None:
    """Load API keys from environment variable."""
    global _API_KEYS
    keys_env = os.getenv("API_KEYS", "")
    if keys_env:
        for key in keys_env.split(","):
            key = key.strip()
            if key:
                _API_KEYS.add(key)
        if _API_KEYS:
            logger.info(f"Loaded {len(_API_KEYS)} API key(s) from environment")


_load_api_keys()


class APIKeyAuth:
    """API Key authentication handler."""
    
    def __init__(self):
        self.api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)
    
    async def __call__(
        self,
        api_key: Optional[str] = None
    ) -> Optional[str]:
        """Validate API key from request header."""
        api_key = await Security(self.api_key_header)
        if not _API_KEYS:
            logger.debug("API authentication disabled - no API keys configured")
            return None
        
        if api_key is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "error": "missing_api_key",
                    "message": f"Missing API key. Include '{API_KEY_NAME}' header in your request.",
                }
            )
        
        if api_key not in _API_KEYS:
            logger.warning(f"Invalid API key attempted: {api_key[:8]}...")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "error": "invalid_api_key",
                    "message": "Invalid API key.",
                }
            )
        
        return api_key


api_key_auth = APIKeyAuth()


async def verify_api_key(
    api_key: Optional[str] = Security(api_key_auth.api_key_header)
) -> Optional[str]:
    """FastAPI dependency for API key verification."""
    return await api_key_auth(api_key)


def reload_api_keys() -> None:
    """Reload API keys from environment variable."""
    global _API_KEYS
    _API_KEYS.clear()
    _load_api_keys()
