"""Base video provider class with common functionality.

Provides the abstract base class for all video provider implementations,
with support for dependency injection via constructor parameters.
"""

from abc import ABC, abstractmethod
from typing import Optional
import httpx
from loguru import logger


class BaseVideoProvider(ABC):
    """Abstract base class for video providers.
    
    Provides common configuration handling and HTTP utilities.
    Subclasses must implement provider-specific logic.
    """
    
    def __init__(self, api_token: str = "", base_url: str = ""):
        """Initialize base provider with configuration.
        
        Args:
            api_token: API key/token for authentication.
            base_url: Base URL for API endpoints.
        """
        self.api_token = api_token
        self.base_url = base_url
        self._headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json",
        } if api_token else {}
    
    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return the name of the provider."""
        pass

    @abstractmethod
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
            aspect_ratio: Video aspect ratio.
            fps: Frames per second.
            quality: Video quality level.
            **kwargs: Additional provider-specific parameters.
            
        Returns:
            Dictionary with task_id and status.
        """
        pass

    @abstractmethod
    async def get_task_status(self, task_id: str) -> dict:
        """Get the status of a video generation task.
        
        Args:
            task_id: The task ID from generate_video.
            
        Returns:
            Dictionary with status and video_url if completed.
        """
        pass

    async def _make_request(self, method: str, url: str, **kwargs) -> dict:
        """Make an HTTP request with error handling.
        
        Args:
            method: HTTP method (GET, POST, etc.).
            url: Full URL for the request.
            **kwargs: Additional arguments for httpx.
            
        Returns:
            Parsed JSON response.
        """
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
