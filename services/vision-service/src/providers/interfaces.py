"""Provider protocol interfaces for video generation services.

This module defines the VideoProvider protocol that all video providers
must implement, enabling dependency injection and testability.
"""

from typing import Protocol, Optional


class VideoProvider(Protocol):
    """Protocol interface for video generation providers.
    
    All video provider implementations must conform to this protocol
    to ensure consistent behavior and enable dependency injection.
    """
    
    @property
    def provider_name(self) -> str:
        """Return the name of the provider."""
        ...
    
    async def generate_video(
        self,
        prompt: str,
        negative_prompt: Optional[str] = None,
        duration: int = 5,
        aspect_ratio: str = "16:9",
        fps: int = 24,
        quality: str = "high",
        **kwargs
    ) -> dict:
        """Generate a video from text prompt.
        
        Args:
            prompt: Text description of the video content.
            negative_prompt: Elements to avoid in the video.
            duration: Video duration in seconds.
            aspect_ratio: Video aspect ratio (e.g., "16:9").
            fps: Frames per second.
            quality: Video quality level.
            **kwargs: Additional provider-specific parameters.
            
        Returns:
            Dictionary with task_id and status.
        """
        ...
    
    async def get_task_status(self, task_id: str) -> dict:
        """Get the status of a video generation task.
        
        Args:
            task_id: The task ID from generate_video.
            
        Returns:
            Dictionary with status and video_url if completed.
        """
        ...
