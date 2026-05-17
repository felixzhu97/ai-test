"""TTS Application Service.

This service orchestrates multiple use cases and provides a unified interface
for the presentation layer (API routes).
"""

from typing import Optional, List, Dict, Any, AsyncIterator

from ..dtos import (
    SynthesizeRequestDTO,
    SynthesizeResponseDTO,
    StreamRequestDTO,
    VoiceDTO,
    ProviderDTO,
    HealthResponseDTO,
)
from ..use_cases import (
    SynthesizeSpeechUseCase,
    SynthesizeSpeechInput,
    StreamSpeechUseCase,
    StreamSpeechInput,
    ListVoicesUseCase,
    ListVoicesInput,
    GetHealthUseCase,
)


class TTSApplicationService:
    """Application service that orchestrates TTS use cases.
    
    This service acts as a facade for the application layer, providing
    a convenient interface for the presentation layer while maintaining
    separation of concerns.
    """
    
    # Provider metadata
    PROVIDERS: Dict[str, Dict[str, Any]] = {
        "azure": {
            "display_name": "Azure Cognitive Services TTS",
            "supported_languages": [
                "en-US", "en-GB", "en-AU", "en-CA", "en-IN",
                "zh-CN", "zh-TW", "zh-HK",
                "ja-JP", "ko-KR",
                "fr-FR", "de-DE", "es-ES", "es-MX",
                "pt-BR", "pt-PT", "it-IT", "ru-RU", "nl-NL",
            ],
            "features": [
                "Neural voices", "Multi-language support",
                "Voice styles", "Pitch/speed adjustment", "SSML support",
            ],
        },
        "google": {
            "display_name": "Google Cloud Text-to-Speech",
            "supported_languages": [
                "en-US", "en-GB", "en-AU",
                "zh-CN", "zh-TW",
                "ja-JP", "ko-KR",
                "fr-FR", "de-DE", "es-ES", "it-IT",
                "pt-BR", "ru-RU", "nl-NL",
            ],
            "features": [
                "WaveNet voices", "DeepMind WaveNet technology",
                "Multi-language support", "SSML support", "Voice selection",
            ],
        },
        "elevenlabs": {
            "display_name": "ElevenLabs",
            "supported_languages": ["en", "zh", "ja", "ko", "de", "fr", "es", "it", "pt", "pl", "nl", "ar"],
            "features": [
                "Ultra-realistic AI voices", "Voice cloning",
                "Emotion control", "Voice conversion", "Multi-language (28+ languages)",
                "Streaming API",
            ],
        },
        "coqui": {
            "display_name": "Coqui TTS (Local)",
            "supported_languages": ["en", "multi"],
            "features": [
                "Open-source", "Local deployment",
                "Privacy-focused", "Voice conversion", "Custom model support",
            ],
        },
        "edge": {
            "display_name": "Microsoft Edge TTS (Neural)",
            "supported_languages": [
                "zh-CN", "zh-TW", "zh-HK",
                "en-US", "en-GB", "en-AU", "en-CA",
                "ja-JP", "ko-KR",
                "fr-FR", "de-DE", "es-ES", "es-MX",
                "pt-BR", "pt-PT", "it-IT", "ru-RU",
                "hi-IN",
            ],
            "features": [
                "Neural voices (Neural suffix)", "No API key required",
                "Multi-language (50+ languages)", "Speed/pitch adjustment",
                "Local TTS (no cloud dependency)",
            ],
        },
    }
    
    def __init__(
        self,
        tts_provider_port,
        config_adapter=None,
        synthesis_service=None,
    ):
        """Initialize application service with dependencies.
        
        Args:
            tts_provider_port: TTS provider port implementation
            config_adapter: Optional configuration adapter
            synthesis_service: Optional synthesis service
        """
        self._provider = tts_provider_port
        self._config = config_adapter
        self._synthesis_service = synthesis_service
        
        # Initialize use cases
        self._synthesize_use_case = SynthesizeSpeechUseCase(
            tts_provider_port=tts_provider_port,
            config_adapter=config_adapter,
            synthesis_service=synthesis_service,
        )
        self._stream_use_case = StreamSpeechUseCase(
            tts_provider_port=tts_provider_port,
            config_adapter=config_adapter,
            synthesis_service=synthesis_service,
        )
        self._list_voices_use_case = ListVoicesUseCase(
            tts_provider_port=tts_provider_port,
            synthesis_service=synthesis_service,
        )
        self._get_health_use_case = GetHealthUseCase(
            tts_provider_port=tts_provider_port,
            config_adapter=config_adapter,
        )

    async def synthesize_speech(self, request: SynthesizeRequestDTO) -> SynthesizeResponseDTO:
        """Synthesize text to speech.
        
        Args:
            request: Synthesis request DTO
            
        Returns:
            SynthesizeResponseDTO with audio data
        """
        input_data = SynthesizeSpeechInput.from_dto(request)
        output = await self._synthesize_use_case.execute(input_data)
        return output.to_dto()

    async def stream_speech(self, request: StreamRequestDTO) -> AsyncIterator[bytes]:
        """Stream synthesized speech.
        
        Args:
            request: Stream request DTO
            
        Yields:
            Audio chunks
        """
        input_data = StreamSpeechInput.from_dto(request)
        async for chunk in self._stream_use_case.execute(input_data):
            yield chunk

    async def list_voices(self, language: Optional[str] = None) -> List[VoiceDTO]:
        """List available voices.
        
        Args:
            language: Optional language filter
            
        Returns:
            List of voice DTOs
        """
        input_data = ListVoicesInput(
            language=language,
            provider=self._get_provider_name(),
        )
        output = await self._list_voices_use_case.execute(input_data)
        return output.to_dto_list()

    async def get_health(self) -> HealthResponseDTO:
        """Get service health status.
        
        Returns:
            Health response DTO
        """
        output = await self._get_health_use_case.execute()
        return output.to_dto()

    async def get_providers(self) -> List[ProviderDTO]:
        """Get all available providers.
        
        Returns:
            List of provider DTOs
        """
        active_provider = self._get_provider_name()
        
        return [
            ProviderDTO(
                name=name,
                display_name=info["display_name"],
                supported_languages=info["supported_languages"],
                features=info["features"],
                is_active=(name == active_provider),
            )
            for name, info in self.PROVIDERS.items()
        ]

    async def get_current_provider(self) -> ProviderDTO:
        """Get current active provider.
        
        Returns:
            Provider DTO for active provider
        """
        providers = await self.get_providers()
        for provider in providers:
            if provider.is_active:
                return provider
        
        # Fallback to first provider
        return providers[0] if providers else ProviderDTO(
            name="unknown",
            display_name="Unknown Provider",
            is_active=True,
        )

    def _get_provider_name(self) -> str:
        """Get current provider name from config."""
        if self._config:
            return self._config.get_provider_name()
        return "edge"
