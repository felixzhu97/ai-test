"""Generate video use case."""

from typing import Optional
from ...domain.entities.video_task import VideoTask, VideoTaskStatus
from ...domain.value_objects.video_config import VideoConfig, AspectRatio, VideoQuality
from ...domain.services.video_generation_service import VideoGenerationService


class GenerateVideoInput:
    """Input for video generation use case."""

    def __init__(
        self,
        prompt: str,
        negative_prompt: Optional[str] = None,
        duration: int = 5,
        aspect_ratio: AspectRatio = AspectRatio.RATIO_16_9,
        fps: int = 24,
        quality: VideoQuality = VideoQuality.HIGH,
        seed: Optional[int] = None,
    ):
        self.prompt = prompt
        self.negative_prompt = negative_prompt
        self.duration = duration
        self.aspect_ratio = aspect_ratio
        self.fps = fps
        self.quality = quality
        self.seed = seed


class GenerateVideoOutput:
    """Output from video generation use case."""

    def __init__(self, task: VideoTask):
        self.task_id = task.task_id
        self.status = task.status.value
        self.message = "Video generation started"


class GenerateVideoUseCase:
    """Application use case for video generation."""

    def __init__(self, service: VideoGenerationService):
        self._service = service

    async def execute(self, input_data: GenerateVideoInput) -> GenerateVideoOutput:
        """Execute the video generation use case."""
        config = VideoConfig(
            duration=input_data.duration,
            aspect_ratio=input_data.aspect_ratio,
            fps=input_data.fps,
            quality=input_data.quality,
            negative_prompt=input_data.negative_prompt,
            seed=input_data.seed,
        )

        task = await self._service.create_task(
            prompt=input_data.prompt,
            config=config,
        )

        return GenerateVideoOutput(task)
