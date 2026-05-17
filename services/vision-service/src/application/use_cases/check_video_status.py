"""Check video status use case."""

from typing import Optional
from ...domain.entities.video_task import VideoTask
from ...domain.services.video_generation_service import VideoGenerationService


class CheckVideoStatusInput:
    """Input for checking video status."""

    def __init__(self, task_id: str):
        self.task_id = task_id


class CheckVideoStatusOutput:
    """Output from checking video status."""

    def __init__(self, task: VideoTask):
        self.task_id = task.task_id
        self.status = task.status.value
        self.video_url = task.video_url
        self.thumbnail_url = task.thumbnail_url
        self.error = task.error_message
        self.processing_time_seconds = task.processing_time_seconds


class CheckVideoStatusUseCase:
    """Application use case for checking video generation status."""

    def __init__(self, service: VideoGenerationService):
        self._service = service

    async def execute(self, input_data: CheckVideoStatusInput) -> CheckVideoStatusOutput:
        """Execute the video status check use case."""
        task = await self._service.get_task_status(input_data.task_id)
        return CheckVideoStatusOutput(task)
