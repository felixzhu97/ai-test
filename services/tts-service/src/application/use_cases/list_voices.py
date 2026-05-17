"""List Voices Use Case.

This use case retrieves available voices from the TTS provider.
"""

from typing import Optional, List
from dataclasses import dataclass

from ...domain.entities import Voice
from ..dtos import VoiceDTO


@dataclass(frozen=True)
class ListVoicesInput:
    """Input value object for list voices use case."""
    language: Optional[str] = None
    provider: Optional[str] = None

    @classmethod
    def with_language(cls, language: str) -> "ListVoicesInput":
        """Create input with language filter."""
        return cls(language=language)

    @classmethod
    def all(cls) -> "ListVoicesInput":
        """Create input for all voices."""
        return cls()


@dataclass(frozen=True)
class ListVoicesOutput:
    """Output value object for list voices use case."""
    voices: List[VoiceDTO]
    total_count: int
    language_filter: Optional[str]

    def to_dto_list(self) -> List[VoiceDTO]:
        """Return voices as DTO list."""
        return self.voices


class ListVoicesUseCase:
    """Use case for listing available voices.
    
    Responsibilities:
    - Retrieve voices from provider
    - Filter by language if specified
    - Transform to DTOs
    """
    
    def __init__(self, tts_provider_port, synthesis_service=None):
        """Initialize use case with dependencies.
        
        Args:
            tts_provider_port: TTS provider port implementation
            synthesis_service: Optional synthesis service for voice filtering
        """
        self._provider = tts_provider_port
        self._synthesis_service = synthesis_service

    async def execute(self, input_data: ListVoicesInput) -> ListVoicesOutput:
        """Execute list voices use case.
        
        Args:
            input_data: Filter parameters
            
        Returns:
            ListVoicesOutput with voice list and metadata
        """
        try:
            # Get voices from provider
            voices = await self._provider.list_voices(
                language=input_data.language
            )
            
            # Additional filtering if synthesis service available
            if self._synthesis_service and (input_data.language or input_data.provider):
                voices = self._synthesis_service.filter_voices(
                    voices,
                    language=input_data.language,
                )
            
            # Transform to DTOs
            voice_dtos = [
                VoiceDTO(
                    id=v.id,
                    name=v.name,
                    language=v.language,
                    language_name=v.language_name,
                    gender=v.gender,
                    provider=v.provider,
                    is_default=v.is_default,
                )
                for v in voices
            ]
            
            return ListVoicesOutput(
                voices=voice_dtos,
                total_count=len(voice_dtos),
                language_filter=input_data.language,
            )
            
        except Exception as e:
            raise RuntimeError(f"Failed to list voices: {str(e)}") from e
