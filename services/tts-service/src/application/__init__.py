"""Application layer for TTS Service.

This module contains the application services, use cases, and DTOs.
"""

from .dtos import (
    SynthesizeRequestDTO,
    SynthesizeResponseDTO,
    StreamRequestDTO,
    VoiceDTO,
    ProviderDTO,
    HealthResponseDTO,
    OutputFormatDTO,
)
from .use_cases import (
    SynthesizeSpeechUseCase,
    SynthesizeSpeechInput,
    SynthesizeSpeechOutput,
    StreamSpeechUseCase,
    StreamSpeechInput,
    ListVoicesUseCase,
    ListVoicesInput,
    ListVoicesOutput,
    GetHealthUseCase,
    GetHealthOutput,
)
from .services import TTSApplicationService

__all__ = [
    # DTOs
    "SynthesizeRequestDTO",
    "SynthesizeResponseDTO",
    "StreamRequestDTO",
    "VoiceDTO",
    "ProviderDTO",
    "HealthResponseDTO",
    "OutputFormatDTO",
    # Use Cases
    "SynthesizeSpeechUseCase",
    "SynthesizeSpeechInput",
    "SynthesizeSpeechOutput",
    "StreamSpeechUseCase",
    "StreamSpeechInput",
    "ListVoicesUseCase",
    "ListVoicesInput",
    "ListVoicesOutput",
    "GetHealthUseCase",
    "GetHealthOutput",
    # Application Service
    "TTSApplicationService",
]
