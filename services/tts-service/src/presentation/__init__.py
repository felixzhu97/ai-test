"""Presentation layer for TTS Service.

This layer contains API routes and HTTP-specific handling.
"""

from .routers import tts_router

__all__ = ["tts_router"]
