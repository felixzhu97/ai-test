"""Video task entity."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List
from enum import Enum
import uuid

from ..events.video_events import (
    VideoTaskCreatedEvent,
    VideoTaskCompletedEvent,
    VideoTaskFailedEvent,
)


class VideoTaskStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class InvalidStateTransitionError(ValueError):
    """Raised when an invalid state transition is attempted."""

    pass


class TaskNotFoundError(ValueError):
    """Raised when a task is not found."""

    pass


@dataclass
class VideoTask:
    """Video generation task entity.

    Encapsulates the business rules for video generation tasks,
    including status transitions and URL generation.
    """

    prompt: str
    status: VideoTaskStatus = VideoTaskStatus.PENDING
    task_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    video_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    processing_time_seconds: Optional[float] = None
    _events: List[object] = field(default_factory=list, repr=False)

    @classmethod
    def created(cls, prompt: str) -> "VideoTask":
        """Factory method to create a new task and publish created event."""
        task = cls(prompt=prompt)
        task._events.append(
            VideoTaskCreatedEvent(
                task_id=task.task_id,
                prompt=task.prompt,
                timestamp=task.created_at,
            )
        )
        return task

    def pop_events(self) -> List[object]:
        """Retrieve and clear all collected domain events."""
        events = self._events.copy()
        self._events.clear()
        return events

    def mark_processing(self) -> None:
        """Transition to processing state."""
        if self.status != VideoTaskStatus.PENDING:
            raise InvalidStateTransitionError(
                f"Cannot transition from {self.status} to PROCESSING"
            )
        self.status = VideoTaskStatus.PROCESSING

    def mark_completed(self, video_url: str, thumbnail_url: Optional[str] = None) -> None:
        """Mark task as completed with URLs."""
        if self.status not in (VideoTaskStatus.PENDING, VideoTaskStatus.PROCESSING):
            raise InvalidStateTransitionError(
                f"Cannot transition from {self.status} to COMPLETED"
            )
        self.status = VideoTaskStatus.COMPLETED
        self.video_url = video_url
        self.thumbnail_url = thumbnail_url
        self.completed_at = datetime.now()
        if self.created_at:
            self.processing_time_seconds = (
                self.completed_at - self.created_at
            ).total_seconds()
        self._events.append(
            VideoTaskCompletedEvent(
                task_id=self.task_id,
                video_url=self.video_url,
                thumbnail_url=self.thumbnail_url,
                processing_time_seconds=self.processing_time_seconds,
                timestamp=self.completed_at,
            )
        )

    def mark_failed(self, error_message: str) -> None:
        """Mark task as failed with error."""
        if self.status == VideoTaskStatus.COMPLETED:
            raise InvalidStateTransitionError("Cannot fail a completed task")
        self.status = VideoTaskStatus.FAILED
        self.error_message = error_message
        self.completed_at = datetime.now()
        self._events.append(
            VideoTaskFailedEvent(
                task_id=self.task_id,
                error_message=self.error_message,
                timestamp=self.completed_at,
            )
        )

    @property
    def is_terminal(self) -> bool:
        """Check if task is in a terminal state."""
        return self.status in (
            VideoTaskStatus.COMPLETED,
            VideoTaskStatus.FAILED,
        )
