"""Provider protocol interfaces for video generation services.

This module re-exports the VideoProvider protocol from the domain layer.
The actual protocol definition is in src.domain.services.video_generation_service.

This module is kept for backward compatibility and internal documentation.
"""

from typing import Protocol

from ...domain.services.video_generation_service import IVideoProvider

# Re-export from domain layer for backward compatibility
VideoProvider = IVideoProvider

__all__ = ["VideoProvider", "IVideoProvider"]
