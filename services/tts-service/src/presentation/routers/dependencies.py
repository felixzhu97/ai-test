"""FastAPI dependencies for TTS Service.

This module provides dependency injection for the presentation layer.
"""

from typing import Annotated, Optional

from ...application import TTSApplicationService
from ...domain import SynthesisService
from ...infrastructure import TTSFactory


class ConfigAdapter:
    """Adapter for accessing configuration settings.
    
    This adapter provides a consistent interface for accessing
    configuration values across the application.
    """
    
    def __init__(self, settings):
        """Initialize with settings object.
        
        Args:
            settings: Pydantic settings object
        """
        self._settings = settings
    
    def get_provider_name(self) -> str:
        """Get current TTS provider name."""
        return self._settings.tts_provider.value
    
    def get_default_voice(self) -> str:
        """Get default voice identifier."""
        return self._settings.default_voice
    
    def get_default_language(self) -> str:
        """Get default language code."""
        return self._settings.default_language
    
    def is_cache_enabled(self) -> bool:
        """Check if caching is enabled."""
        return self._settings.enable_cache
    
    def get(self, key: str, default=None):
        """Get a configuration value by key."""
        return getattr(self._settings, key, default)


# Global factory instance
_tts_factory: Optional[TTSFactory] = None
_config_adapter: Optional[ConfigAdapter] = None


def init_dependencies(settings):
    """Initialize global dependencies.
    
    Call this during application startup.
    
    Args:
        settings: Pydantic settings object
    """
    global _tts_factory, _config_adapter
    
    _config_adapter = ConfigAdapter(settings)
    _tts_factory = TTSFactory(config_adapter=_config_adapter)


def get_tts_factory() -> TTSFactory:
    """Get TTS factory instance."""
    global _tts_factory
    if _tts_factory is None:
        _tts_factory = TTSFactory()
    return _tts_factory


def get_config_adapter() -> Optional[ConfigAdapter]:
    """Get config adapter instance."""
    global _config_adapter
    return _config_adapter


def get_synthesis_service() -> SynthesisService:
    """Get synthesis service instance."""
    config = get_config_adapter()
    default_voice = config.get_default_voice() if config else "en-US-JennyNeural"
    default_language = config.get_default_language() if config else "en-US"
    return SynthesisService(
        default_voice=default_voice,
        default_language=default_language,
    )


async def get_tts_application_service() -> TTSApplicationService:
    """Get TTS application service.
    
    This is a FastAPI dependency that creates an application service
    with all required dependencies injected.
    
    Returns:
        TTSApplicationService instance
    """
    factory = get_tts_factory()
    config = get_config_adapter()
    synthesis_service = get_synthesis_service()
    
    # Get current provider
    provider_name = config.get_provider_name() if config else "edge"
    provider = factory.get_provider(provider_name)
    
    return TTSApplicationService(
        tts_provider_port=provider,
        config_adapter=config,
        synthesis_service=synthesis_service,
    )


# Type aliases for dependency injection
TTSServiceDep = Annotated[TTSApplicationService, None]
ConfigDep = Annotated[Optional[ConfigAdapter], None]
SynthesisServiceDep = Annotated[SynthesisService, None]
