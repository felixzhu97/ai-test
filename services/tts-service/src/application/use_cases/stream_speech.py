"""Stream Speech Use Case.

This use case handles streaming speech synthesis for real-time audio delivery.
"""

from typing import Optional, Dict, Any, AsyncIterator
from dataclasses import dataclass

from ...domain.entities import SynthesisRequest, OutputFormat
from ..dtos import StreamRequestDTO


@dataclass(frozen=True)
class StreamSpeechInput:
    """Input value object for streaming synthesis use case."""
    text: str
    voice: Optional[str] = None
    language: Optional[str] = None
    speed: float = 1.0
    output_format: str = "mp3"

    @classmethod
    def from_dto(cls, dto: StreamRequestDTO) -> "StreamSpeechInput":
        """Create input from DTO."""
        return cls(
            text=dto.text,
            voice=dto.voice,
            language=dto.language,
            speed=dto.speed,
            output_format=dto.output_format.value,
        )


class StreamSpeechUseCase:
    """Use case for streaming speech synthesis.
    
    Responsibilities:
    - Validate streaming parameters
    - Return async iterator for audio chunks
    - Handle streaming errors gracefully
    """
    
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

    async def execute(self, input_data: StreamSpeechInput) -> AsyncIterator[bytes]:
        """Execute streaming synthesis.
        
        Args:
            input_data: Validated streaming parameters
            
        Yields:
            Audio data chunks
            
        Raises:
            ValueError: If input validation fails
        """
        # Validate text
        if not input_data.text or not input_data.text.strip():
            raise ValueError("Text cannot be empty")
        
        if len(input_data.text) > 10000:
            raise ValueError("Text exceeds maximum length of 10000 characters")
        
        # Normalize text if synthesis service available
        text = input_data.text
        if self._synthesis_service:
            text = self._synthesis_service.normalize_text(text)
        
        # Apply defaults
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
            pitch=0,  # Streaming doesn't support pitch
            output_format=output_format,
        )
        
        try:
            # Stream audio chunks
            async for chunk in self._provider.stream(request):
                yield chunk
                
        except Exception as e:
            raise RuntimeError(f"Streaming synthesis failed: {str(e)}") from e

    def _map_output_format(self, format_str: str) -> OutputFormat:
        """Map string format to domain OutputFormat."""
        try:
            return OutputFormat.from_string(format_str)
        except ValueError:
            return OutputFormat.MP3
