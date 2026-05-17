"""Video generation domain service."""

from typing import Protocol, Optional
from ..entities.video_task import VideoTask, VideoTaskStatus
from ..value_objects.video_config import VideoConfig


class VideoProvider(Protocol):
    """Protocol for video generation providers."""

    @property
    def provider_name(self) -> str: ...

    async def generate_video(self, prompt: str, **kwargs) -> dict: ...
    async def get_task_status(self, task_id: str) -> dict: ...


class VideoGenerationService:
    """Domain service for video generation orchestration."""

    def __init__(self, provider: VideoProvider):
        self._provider = provider

    async def create_task(
        self,
        prompt: str,
        config: VideoConfig,
    ) -> VideoTask:
        """Create a new video generation task."""
        if not prompt.strip():
            raise ValueError("Prompt cannot be empty")

        result = await self._provider.generate_video(
            prompt=prompt,
            negative_prompt=config.negative_prompt,
            duration=config.duration,
            aspect_ratio=config.aspect_ratio.value,
            fps=config.fps,
            quality=config.quality.value,
        )

        return VideoTask(
            task_id=result["task_id"],
            prompt=prompt,
            status=VideoTaskStatus.PENDING,
        )

    async def get_task_status(self, task_id: str) -> VideoTask:
        """Get updated task status from provider."""
        if not task_id:
            raise ValueError("Task ID cannot be empty")

        result = await self._provider.get_task_status(task_id)

        task = VideoTask(
            task_id=task_id,
            prompt="",  # Not returned by status check
            status=result["status"],
        )

        if result["status"] == "completed":
            task.mark_completed(
                video_url=result.get("video_url", ""),
                thumbnail_url=result.get("thumbnail_url"),
            )
        elif result["status"] == "failed":
            task.mark_failed(result.get("error", "Unknown error"))

        return task
