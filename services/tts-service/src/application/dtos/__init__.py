"""Data Transfer Objects for TTS Application Layer."""

from .synthesis_dto import (
    SynthesizeRequestDTO,
    SynthesizeResponseDTO,
    StreamRequestDTO,
    VoiceDTO,
    ProviderDTO,
    HealthResponseDTO,
    OutputFormatDTO,
)

__all__ = [
    "SynthesizeRequestDTO",
    "SynthesizeResponseDTO",
    "StreamRequestDTO",
    "VoiceDTO",
    "ProviderDTO",
    "HealthResponseDTO",
    "OutputFormatDTO",
]
