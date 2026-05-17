"""Video provider factory and exports.

This module provides a factory function for creating video provider instances
with dependency injection support.
"""

from .base import BaseVideoProvider
from .mock import MockVideoProvider
from .replicate import ReplicateVideoProvider
from .kling import KlingVideoProvider
from .runway import RunwayVideoProvider
from .pika import PikaVideoProvider
from .sora import SoraVideoProvider
from ..core.config import VideoProvider

__all__ = [
    "BaseVideoProvider",
    "MockVideoProvider",
    "ReplicateVideoProvider",
    "KlingVideoProvider",
    "RunwayVideoProvider",
    "PikaVideoProvider",
    "SoraVideoProvider",
    "get_provider",
]


def get_provider(
    provider_name: str = None,
    api_key: str = "",
    api_secret: str = "",
) -> BaseVideoProvider:
    """Factory function to create video providers.
    
    Supports dependency injection by accepting API credentials as parameters,
    enabling easy mocking in unit tests.
    
    Args:
        provider_name: Provider name (defaults to settings.VIDEO_PROVIDER).
        api_key: API key for the provider.
        api_secret: API secret (for Kling).
        
    Returns:
        Configured provider instance.
    """
    from ..core.config import get_settings
    
    if provider_name is None:
        settings = get_settings()
        provider_name = settings.VIDEO_PROVIDER

    provider_map = {
        VideoProvider.MOCK: MockVideoProvider,
        VideoProvider.REPLICATE: ReplicateVideoProvider,
        VideoProvider.KLING: KlingVideoProvider,
        VideoProvider.RUNWAY: RunwayVideoProvider,
        VideoProvider.PIKA: PikaVideoProvider,
        VideoProvider.SORA: SoraVideoProvider,
    }
    
    provider_class = provider_map.get(provider_name, MockVideoProvider)
    
    # Pass appropriate credentials based on provider type
    if provider_name == VideoProvider.KLING:
        return provider_class(api_key=api_key, api_secret=api_secret)
    elif provider_name == VideoProvider.REPLICATE:
        return provider_class(api_token=api_key)
    elif provider_name in (VideoProvider.PIKA, VideoProvider.RUNWAY, VideoProvider.SORA):
        return provider_class(api_key=api_key)
    else:
        return provider_class()
