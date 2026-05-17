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
from .image_gen_dtos import (
    GenerateImageInputDTO,
    GenerateImageOutputDTO,
    GenerateVariationInputDTO,
    GenerateVariationOutputDTO,
    UpscaleImageInputDTO,
    UpscaleImageOutputDTO,
    ListModelsOutputDTO,
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
    # Image Gen DTOs
    "GenerateImageInputDTO",
    "GenerateImageOutputDTO",
    "GenerateVariationInputDTO",
    "GenerateVariationOutputDTO",
    "UpscaleImageInputDTO",
    "UpscaleImageOutputDTO",
    "ListModelsOutputDTO",
    # Vision DTOs
    "TaskType",
    "DetectionResult",
    "DetectionResponseDTO",
    "CaptionResponseDTO",
    "OCRResult",
    "OCRResponseDTO",
]
