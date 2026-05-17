"""DTOs for TTS synthesis operations.

These DTOs act as the bridge between the API layer and application layer.
They are pure data containers with validation, keeping the use cases free of HTTP concerns.
"""

from typing import Optional, List, Dict, Any, AsyncIterator
from enum import Enum

from pydantic import BaseModel, Field, field_validator


class OutputFormatDTO(str, Enum):
    """Supported audio output formats."""
    MP3 = "mp3"
    WAV = "wav"
    OGG = "ogg"
    FLAC = "flac"


class AudioConfigDTO(BaseModel):
    """Audio configuration settings."""
    sample_rate: Optional[int] = Field(
        default=24000,
        ge=8000,
        le=48000,
        description="Audio sample rate in Hz"
    )
    bit_rate: Optional[int] = Field(
        default=128,
        description="Audio bit rate in kbps"
    )
    channels: int = Field(default=1, description="Number of audio channels")

    class Config:
        frozen = True


class SynthesizeRequestDTO(BaseModel):
    """Request DTO for text synthesis.
    
    This DTO validates incoming API requests before passing them to use cases.
    """
    text: str = Field(
        ...,
        min_length=1,
        max_length=10000,
        description="Text to synthesize"
    )
    voice: Optional[str] = Field(
        default=None,
        description="Voice identifier"
    )
    language: Optional[str] = Field(
        default=None,
        description="Language code (e.g., en-US)"
    )
    speed: float = Field(
        default=1.0,
        ge=0.25,
        le=4.0,
        description="Speech speed multiplier"
    )
    pitch: float = Field(
        default=0,
        ge=-20,
        le=20,
        description="Voice pitch adjustment in Hz"
    )
    output_format: OutputFormatDTO = Field(
        default=OutputFormatDTO.MP3,
        description="Audio output format"
    )
    audio_config: Optional[AudioConfigDTO] = Field(
        default=None,
        description="Audio configuration"
    )
    
    @field_validator('text')
    @classmethod
    def validate_text_not_empty(cls, v: str) -> str:
        """Ensure text is not just whitespace."""
        if not v.strip():
            raise ValueError("Text cannot be empty or whitespace only")
        return v

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for domain layer."""
        return {
            "text": self.text,
            "voice": self.voice,
            "language": self.language,
            "speed": self.speed,
            "pitch": self.pitch,
            "output_format": self.output_format.value,
            "audio_config": self.audio_config.model_dump() if self.audio_config else None,
        }


class SynthesizeResponseDTO(BaseModel):
    """Response DTO for synthesis operation."""
    audio_data: bytes = Field(..., description="Synthesized audio data")
    content_type: str = Field(..., description="Audio content type (MIME)")
    filename: str = Field(..., description="Suggested filename")
    duration_seconds: Optional[float] = Field(None, description="Audio duration in seconds")
    format: OutputFormatDTO = Field(..., description="Audio format")
    size_bytes: int = Field(..., description="Audio data size in bytes")

    class Config:
        frozen = True


class StreamRequestDTO(BaseModel):
    """Request DTO for streaming synthesis.
    
    Streaming requests have reduced parameters since streaming typically
    doesn't support all synthesis options.
    """
    text: str = Field(
        ...,
        min_length=1,
        max_length=10000,
        description="Text to synthesize"
    )
    voice: Optional[str] = Field(default=None, description="Voice identifier")
    language: Optional[str] = Field(default=None, description="Language code")
    speed: float = Field(default=1.0, ge=0.25, le=4.0)
    output_format: OutputFormatDTO = Field(default=OutputFormatDTO.MP3)
    
    @field_validator('text')
    @classmethod
    def validate_text_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Text cannot be empty or whitespace only")
        return v

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for domain layer."""
        return {
            "text": self.text,
            "voice": self.voice,
            "language": self.language,
            "speed": self.speed,
            "output_format": self.output_format.value,
        }


class VoiceDTO(BaseModel):
    """Voice information DTO."""
    id: str = Field(..., description="Voice identifier")
    name: str = Field(..., description="Voice name")
    language: str = Field(..., description="Language code")
    language_name: Optional[str] = Field(None, description="Language display name")
    gender: Optional[str] = Field(None, description="Voice gender")
    provider: str = Field(..., description="TTS provider name")
    is_default: bool = Field(default=False, description="Is default voice")

    class Config:
        frozen = True


class ProviderDTO(BaseModel):
    """Provider information DTO."""
    name: str = Field(..., description="Provider name")
    display_name: str = Field(..., description="Provider display name")
    supported_languages: List[str] = Field(
        default_factory=list,
        description="Supported language codes"
    )
    features: List[str] = Field(
        default_factory=list,
        description="Provider features"
    )
    is_active: bool = Field(default=False, description="Is currently active")

    class Config:
        frozen = True


class HealthResponseDTO(BaseModel):
    """Health check response DTO."""
    status: str = Field(..., description="Service status (healthy/degraded/unhealthy)")
    provider: str = Field(..., description="Active provider name")
    provider_status: str = Field(..., description="Provider health status")
    version: str = Field(..., description="Service version")
    components: Optional[Dict[str, str]] = Field(
        None,
        description="Additional component statuses"
    )

    class Config:
        frozen = True
