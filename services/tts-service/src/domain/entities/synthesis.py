"""Synthesis entities - request and result models."""

from dataclasses import dataclass
from enum import Enum
from typing import Optional

from .audio_config import AudioConfig


class OutputFormat(str, Enum):
    """Supported audio output formats."""
    MP3 = "mp3"
    WAV = "wav"
    OGG = "ogg"
    FLAC = "flac"
    
    @classmethod
    def from_string(cls, value: str) -> "OutputFormat":
        """Create OutputFormat from string value.
        
        Args:
            value: Format string (case-insensitive)
            
        Returns:
            OutputFormat enum value
            
        Raises:
            ValueError: If format is not supported
        """
        value_lower = value.lower()
        for fmt in cls:
            if fmt.value == value_lower:
                return fmt
        raise ValueError(f"Unsupported output format: {value}")
    
    def to_mime_type(self) -> str:
        """Get MIME type for this format.
        
        Returns:
            MIME type string
        """
        mime_types = {
            OutputFormat.MP3: "audio/mpeg",
            OutputFormat.WAV: "audio/wav",
            OutputFormat.OGG: "audio/ogg",
            OutputFormat.FLAC: "audio/flac",
        }
        return mime_types.get(self, "audio/mpeg")


@dataclass(frozen=True)
class SynthesisRequest:
    """Request to synthesize text to speech.
    
    This is the core domain entity representing a synthesis request.
    It contains all the parameters needed for speech synthesis.
    
    Attributes:
        text: The text to synthesize
        voice: Voice identifier (optional, uses default if not specified)
        language: Language code (optional, auto-detected if not specified)
        speed: Speech speed multiplier (0.25-4.0)
        pitch: Pitch adjustment in Hz (-20 to +20)
        output_format: Desired audio output format
        audio_config: Optional audio configuration
    """
    text: str
    voice: Optional[str] = None
    language: Optional[str] = None
    speed: float = 1.0
    pitch: float = 0.0
    output_format: OutputFormat = OutputFormat.MP3
    audio_config: Optional[AudioConfig] = None
    
    def __post_init__(self):
        """Validate synthesis request after initialization."""
        if not self.text or not self.text.strip():
            raise ValueError("Synthesis text cannot be empty")
        if len(self.text) > 10000:
            raise ValueError("Synthesis text exceeds maximum length of 10000 characters")
        if not 0.25 <= self.speed <= 4.0:
            raise ValueError(f"Speed must be between 0.25 and 4.0, got {self.speed}")
        if not -20 <= self.pitch <= 20:
            raise ValueError(f"Pitch must be between -20 and 20, got {self.pitch}")
    
    @classmethod
    def create(
        cls,
        text: str,
        voice: Optional[str] = None,
        language: Optional[str] = None,
        speed: float = 1.0,
        pitch: float = 0.0,
        output_format: str = "mp3",
        audio_config: Optional[dict] = None,
    ) -> "SynthesisRequest":
        """Factory method to create SynthesisRequest.
        
        Args:
            text: Text to synthesize
            voice: Voice identifier
            language: Language code
            speed: Speech speed multiplier
            pitch: Pitch adjustment
            output_format: Output format string
            audio_config: Audio configuration dictionary
            
        Returns:
            SynthesisRequest instance
        """
        fmt = OutputFormat.from_string(output_format) if isinstance(output_format, str) else output_format
        config = AudioConfig.from_dict(audio_config) if audio_config else None
        
        return cls(
            text=text,
            voice=voice,
            language=language,
            speed=speed,
            pitch=pitch,
            output_format=fmt,
            audio_config=config,
        )
    
    def with_defaults(
        self,
        default_voice: str,
        default_language: str,
    ) -> "SynthesisRequest":
        """Create a copy with default values applied.
        
        Args:
            default_voice: Default voice to use if not specified
            default_language: Default language to use if not specified
            
        Returns:
            New SynthesisRequest with defaults applied
        """
        from dataclasses import replace
        return replace(
            self,
            voice=self.voice or default_voice,
            language=self.language or default_language,
        )


@dataclass(frozen=True)
class SynthesisResult:
    """Result of a synthesis operation.
    
    Attributes:
        audio_data: Raw audio bytes
        format: Output format used
        duration_seconds: Audio duration (if available)
        provider: Provider that generated the audio
    """
    audio_data: bytes
    format: OutputFormat
    duration_seconds: Optional[float] = None
    provider: str = "unknown"
    
    def __post_init__(self):
        """Validate synthesis result after initialization."""
        if not self.audio_data:
            raise ValueError("Audio data cannot be empty")
    
    @property
    def size_bytes(self) -> int:
        """Get audio data size in bytes."""
        return len(self.audio_data)
    
    @property
    def content_type(self) -> str:
        """Get MIME content type."""
        return self.format.to_mime_type()
