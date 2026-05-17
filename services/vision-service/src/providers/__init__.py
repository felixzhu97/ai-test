"""Provider module - DEPRECATED.

This module is kept for backward compatibility.
Providers have been moved to the infrastructure layer.

OLD PATH: src/providers/
NEW PATH: src/infrastructure/providers/

Please update your imports:
    Old: from src.providers import get_provider
    New: from src.infrastructure.providers import get_provider

This module will be removed in a future version.
"""

import warnings
warnings.warn(
    "src.providers is deprecated. Please use src.infrastructure.providers instead.",
    DeprecationWarning,
    stacklevel=2
)

# Re-export from new location for backward compatibility
from ..infrastructure.providers import (
    get_provider,
    BaseVideoProvider,
    MockVideoProvider,
    ReplicateVideoProvider,
    KlingVideoProvider,
    RunwayVideoProvider,
    PikaVideoProvider,
    SoraVideoProvider,
    IVideoProvider,
)

__all__ = [
    "BaseVideoProvider",
    "MockVideoProvider",
    "ReplicateVideoProvider",
    "KlingVideoProvider",
    "RunwayVideoProvider",
    "PikaVideoProvider",
    "SoraVideoProvider",
    "get_provider",
    "IVideoProvider",
]
