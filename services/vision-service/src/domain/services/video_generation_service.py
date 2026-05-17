"""Video generation domain service.

This module defines the domain service interface for video generation.
The interface is a Protocol (duck-typed) - implementations must be provided
by the infrastructure layer.

Domain layer rules:
- No async I/O operations
- No direct provider references
- Only business logic validation
"""

from typing import Protocol, Optional
from ..entities.video_task import VideoTask, VideoTaskStatus
from ..value_objects.video_config import VideoConfig


class IVideoProvider(Protocol):
    """Protocol for video generation providers (infrastructure concern).

    This protocol defines the interface that video providers must implement.
    Providers are infrastructure concerns and handle actual HTTP calls.
    """

    @property
    def provider_name(self) -> str: ...

    async def generate_video(self, prompt: str, **kwargs) -> dict: ...
    async def get_task_status(self, task_id: str) -> dict: ...


class IVideoGenerationService(Protocol):
    """Protocol for video generation service (application/infrastructure layer).

    Defines the interface for video generation operations.
    Concrete implementation resides in infrastructure layer.
    """

    async def create_task(
        self,
        prompt: str,
        config: VideoConfig,
    ) -> VideoTask:
        """Create a new video generation task."""
        ...

    async def get_task_status(self, task_id: str) -> VideoTask:
        """Get updated task status from provider."""
        ...


class VideoGenerationService:
    """Pure domain service for video generation validation.

    This class contains only synchronous business logic validation.
    No async operations or infrastructure dependencies are allowed.

    For actual video generation, use VideoGenerationServiceImpl from
    the infrastructure layer.
    """

    @staticmethod
    def validate_prompt(prompt: str) -> None:
        """Validate video generation prompt.

        Raises:
            ValueError: If prompt is empty or invalid.
        """
        if not prompt or not prompt.strip():
            raise ValueError("Prompt cannot be empty")

    @staticmethod
    def validate_task_id(task_id: str) -> None:
        """Validate task ID.

        Raises:
            ValueError: If task_id is empty or invalid.
        """
        if not task_id or not task_id.strip():
            raise ValueError("Task ID cannot be empty")
