"""Application DTOs."""

from .video_dtos import (
    VideoGenerationRequestDTO,
    VideoGenerationResponseDTO,
    VideoTaskStatusDTO,
)
from .image_dtos import (
    ImageGenerationRequestDTO,
    ImageGenerationResponseDTO,
)
from .vision_dtos import (
    TaskType,
    DetectionResult,
    DetectionResponseDTO,
    CaptionResponseDTO,
    OCRResult,
    OCRResponseDTO,
)

__all__ = [
    # Video DTOs
    "VideoGenerationRequestDTO",
    "VideoGenerationResponseDTO",
    "VideoTaskStatusDTO",
    # Image DTOs
    "ImageGenerationRequestDTO",
    "ImageGenerationResponseDTO",
    # Vision DTOs
    "TaskType",
    "DetectionResult",
    "DetectionResponseDTO",
    "CaptionResponseDTO",
    "OCRResult",
    "OCRResponseDTO",
]
