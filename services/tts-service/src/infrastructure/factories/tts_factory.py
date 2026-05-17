"""TTS Factory - creates and manages TTS provider adapters."""

from typing import Optional, Dict, Type
from functools import lru_cache

from ..adapters.base_adapter import BaseTTSAdapter
from ..adapters.edge_tts_adapter import EdgeTTSAdapter
from ..adapters.azure_tts_adapter import AzureTTSAdapter
from ..adapters.google_tts_adapter import GoogleTTSAdapter
from ..adapters.elevenlabs_tts_adapter import ElevenLabsTTSAdapter
from ..adapters.coqui_tts_adapter import CoquiTTSAdapter


class TTSFactory:
    """Factory for creating TTS provider adapters.
    
    Implements singleton pattern to cache adapter instances.
    """
    
    # Provider name to adapter class mapping
    PROVIDERS: Dict[str, Type[BaseTTSAdapter]] = {
        "edge": EdgeTTSAdapter,
        "azure": AzureTTSAdapter,
        "google": GoogleTTSAdapter,
        "elevenlabs": ElevenLabsTTSAdapter,
        "coqui": CoquiTTSAdapter,
    }
    
    def __init__(
        self,
        config_adapter=None,
    ):
        """Initialize factory.
        
        Args:
            config_adapter: Configuration adapter for provider settings
        """
        self._config = config_adapter
        self._adapters: Dict[str, BaseTTSAdapter] = {}
    
    def get_provider(self, provider_name: Optional[str] = None) -> BaseTTSAdapter:
        """Get or create a TTS provider adapter.
        
        Args:
            provider_name: Provider name (uses config default if not specified)
            
        Returns:
            TTS provider adapter instance
            
        Raises:
            ValueError: If provider is not supported
        """
        # Get provider name from config if not specified
        if provider_name is None:
            provider_name = self._get_default_provider()
        
        # Return cached adapter if available
        if provider_name in self._adapters:
            return self._adapters[provider_name]
        
        # Create new adapter
        adapter = self._create_adapter(provider_name)
        self._adapters[provider_name] = adapter
        return adapter
    
    def _create_adapter(self, provider_name: str) -> BaseTTSAdapter:
        """Create a new adapter instance.
        
        Args:
            provider_name: Provider name
            
        Returns:
            New adapter instance
            
        Raises:
            ValueError: If provider is not supported
        """
        if provider_name not in self.PROVIDERS:
            available = ", ".join(self.PROVIDERS.keys())
            raise ValueError(
                f"Unknown provider: {provider_name}. Available: {available}"
            )
        
        adapter_class = self.PROVIDERS[provider_name]
        
        # Get provider-specific config
        config = self._get_provider_config(provider_name)
        
        # Create adapter with config
        return adapter_class(**config)
    
    def _get_default_provider(self) -> str:
        """Get default provider from config."""
        if self._config:
            return self._config.get_provider_name()
        return "edge"
    
    def _get_provider_config(self, provider_name: str) -> Dict:
        """Get configuration for a specific provider.
        
        Args:
            provider_name: Provider name
            
        Returns:
            Configuration dictionary
        """
        config = {}
        
        if self._config:
            # Get provider-specific settings
            if provider_name == "azure":
                config["speech_key"] = self._config.get("azure_speech_key")
                config["speech_region"] = self._config.get("azure_speech_region", "eastus")
            elif provider_name == "google":
                config["credentials_path"] = self._config.get("google_application_credentials")
            elif provider_name == "elevenlabs":
                config["api_key"] = self._config.get("elevenlabs_api_key")
            elif provider_name == "coqui":
                config["model_path"] = self._config.get("coqui_model_path")
            
            # Get default voice
            config["default_voice"] = self._config.get_default_voice()
        
        return config
    
    def list_providers(self) -> list:
        """List available provider names."""
        return list(self.PROVIDERS.keys())
    
    def clear_cache(self):
        """Clear cached adapters."""
        self._adapters.clear()


# Global factory instance
_factory_instance: Optional[TTSFactory] = None


@lru_cache(maxsize=1)
def get_tts_factory() -> TTSFactory:
    """Get global TTS factory instance."""
    global _factory_instance
    if _factory_instance is None:
        _factory_instance = TTSFactory()
    return _factory_instance


def reset_tts_factory():
    """Reset global factory instance (useful for testing)."""
    global _factory_instance
    _factory_instance = None
    get_tts_factory.cache_clear()
