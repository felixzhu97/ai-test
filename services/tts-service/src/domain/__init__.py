"""Domain layer for TTS Service.

This layer contains the core business logic, entities, and domain services.
It is independent of any external frameworks or infrastructure.
"""

from .entities import Voice, AudioConfig, SynthesisRequest, SynthesisResult, OutputFormat
from .ports import TTSProviderPort
from .services import SynthesisService

__all__ = [
 "Voice",
 "AudioConfig",
 "SynthesisRequest",
 "SynthesisResult",
 "OutputFormat",
 "TTSProviderPort",
 "SynthesisService",
]
