"""Domain ports - interfaces for external dependencies."""

from .tts_provider import (
    TTSProviderPort,
    TTSProviderError,
    SynthesisError,
    StreamingError,
    ProviderUnavailableError,
)

__all__ = [
    "TTSProviderPort",
    "TTSProviderError",
    "SynthesisError",
    "StreamingError",
    "ProviderUnavailableError",
]
