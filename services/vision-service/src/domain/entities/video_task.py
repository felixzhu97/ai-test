"""Video task entity."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from enum import Enum
import uuid


class VideoTaskStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class InvalidStateTransitionError(ValueError):
    """Raised when an invalid state transition is attempted."""

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

    def mark_failed(self, error_message: str) -> None:
        """Mark task as failed with error."""
        if self.status == VideoTaskStatus.COMPLETED:
            raise InvalidStateTransitionError("Cannot fail a completed task")
        self.status = VideoTaskStatus.FAILED
        self.error_message = error_message
        self.completed_at = datetime.now()

    @property
    def is_terminal(self) -> bool:
        """Check if task is in a terminal state."""
        return self.status in (
            VideoTaskStatus.COMPLETED,
            VideoTaskStatus.FAILED,
        )
