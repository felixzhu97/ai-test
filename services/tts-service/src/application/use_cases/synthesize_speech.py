"""Synthesize Speech Use Case.

This use case handles the core business logic of converting text to speech.
"""

from typing import Optional, Dict, Any
from dataclasses import dataclass

from ...domain.entities import SynthesisRequest, OutputFormat
from ..dtos import SynthesizeRequestDTO, SynthesizeResponseDTO, OutputFormatDTO


@dataclass(frozen=True)
class SynthesizeSpeechInput:
    """Input value object for synthesis use case."""
    text: str
    voice: Optional[str] = None
    language: Optional[str] = None
    speed: float = 1.0
    pitch: float = 0.0
    output_format: str = "mp3"
    audio_config: Optional[Dict[str, Any]] = None

    @classmethod
    def from_dto(cls, dto: SynthesizeRequestDTO) -> "SynthesizeSpeechInput":
        """Create input from DTO."""
        return cls(
            text=dto.text,
            voice=dto.voice,
            language=dto.language,
            speed=dto.speed,
            pitch=dto.pitch,
            output_format=dto.output_format.value,
            audio_config=dto.audio_config.model_dump() if dto.audio_config else None,
        )


@dataclass(frozen=True)
class SynthesizeSpeechOutput:
    """Output value object for synthesis use case."""
    audio_data: bytes
    content_type: str
    filename: str
    duration_seconds: Optional[float] = None
    format: str = "mp3"

    def to_dto(self) -> SynthesizeResponseDTO:
        """Convert to response DTO."""
        return SynthesizeResponseDTO(
            audio_data=self.audio_data,
            content_type=self.content_type,
            filename=self.filename,
            duration_seconds=self.duration_seconds,
            format=OutputFormatDTO(self.format),
            size_bytes=len(self.audio_data),
        )


class SynthesizeSpeechUseCase:
    """Use case for synthesizing text to speech.
    
    Responsibilities:
    - Validate input parameters
    - Apply default values from configuration
    - Call domain service for synthesis
    - Handle provider errors
    - Return properly formatted response
    """
    
    # Content type mapping
    CONTENT_TYPES = {
        "mp3": "audio/mpeg",
        "wav": "audio/wav",
        "ogg": "audio/ogg",
        "flac": "audio/flac",
    }
    
    def __init__(self, tts_provider_port, config_adapter=None, synthesis_service=None):
        """Initialize use case with dependencies.
        
        Args:
            tts_provider_port: TTS provider port implementation
            config_adapter: Optional configuration adapter for defaults
            synthesis_service: Optional synthesis service for text normalization
        """
        self._provider = tts_provider_port
        self._config = config_adapter
        self._synthesis_service = synthesis_service

    async def execute(self, input_data: SynthesizeSpeechInput) -> SynthesizeSpeechOutput:
        """Execute the synthesis use case.
        
        Args:
            input_data: Validated input parameters
            
        Returns:
            SynthesizeSpeechOutput with audio data and metadata
            
        Raises:
            ValueError: If input validation fails
            RuntimeError: If synthesis fails
        """
        # Validate text length
        if not input_data.text or not input_data.text.strip():
            raise ValueError("Text cannot be empty")
        
        if len(input_data.text) > 10000:
            raise ValueError("Text exceeds maximum length of 10000 characters")
        
        # Normalize text if synthesis service available
        text = input_data.text
        if self._synthesis_service:
            text = self._synthesis_service.normalize_text(text)
        
        # Apply defaults from config if available
        voice = input_data.voice
        language = input_data.language
        
        if self._config:
            voice = voice or self._config.get_default_voice()
            language = language or self._config.get_default_language()
        
        # Map output format
        output_format = self._map_output_format(input_data.output_format)
        
        # Create domain request
        request = SynthesisRequest(
            text=text,
            voice=voice,
            language=language,
            speed=input_data.speed,
            pitch=input_data.pitch,
            output_format=output_format,
        )
        
        try:
            # Call provider through port
            result = await self._provider.synthesize(request)
            
            # Generate response
            content_type = self.CONTENT_TYPES.get(output_format.value, "audio/mpeg")
            filename = f"speech_{hash(text) % 10000}.{output_format.value}"
            
            return SynthesizeSpeechOutput(
                audio_data=result.audio_data,
                content_type=content_type,
                filename=filename,
                duration_seconds=result.duration_seconds,
                format=output_format.value,
            )
            
        except Exception as e:
            raise RuntimeError(f"Speech synthesis failed: {str(e)}") from e

    def _map_output_format(self, format_str: str) -> OutputFormat:
        """Map string format to domain OutputFormat."""
        try:
            return OutputFormat.from_string(format_str)
        except ValueError:
            return OutputFormat.MP3
