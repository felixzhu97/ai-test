"""Infrastructure layer for TTS Service.

This layer contains adapters that implement domain ports using external services.
"""

from .factories.tts_factory import TTSFactory, get_tts_factory

__all__ = [
    "TTSFactory",
    "get_tts_factory",
]
