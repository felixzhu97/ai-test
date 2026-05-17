"""Video events."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class VideoTaskCreatedEvent:
    """Event raised when a video task is created."""

    task_id: str
    prompt: str
    timestamp: datetime


@dataclass
class VideoTaskCompletedEvent:
    """Event raised when a video task completes."""

    task_id: str
    video_url: str
    thumbnail_url: Optional[str]
    processing_time_seconds: float
    timestamp: datetime


@dataclass
class VideoTaskFailedEvent:
    """Event raised when a video task fails."""

    task_id: str
    error_message: str
    timestamp: datetime
