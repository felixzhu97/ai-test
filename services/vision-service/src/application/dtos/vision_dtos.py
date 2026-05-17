"""Vision-related DTOs for API requests and responses."""

from typing import Optional, List
from enum import Enum
from pydantic import BaseModel, Field


class TaskType(str, Enum):
    """Vision task types."""
    DETECT_OBJECTS = "detect_objects"
    CAPTION_IMAGE = "caption_image"
    EXTRACT_TEXT = "extract_text"
    ANALYZE_IMAGE = "analyze_image"


class DetectionResult(BaseModel):
    """Detection result for a single object."""
    class_name: str
    confidence: float = Field(ge=0.0, le=1.0)
    bbox: tuple[int, int, int, int]


class DetectionResponseDTO(BaseModel):
    """DTO for object detection response."""
    task: str = "detect_objects"
    model: str
    detections: List[DetectionResult]
    image_width: int
    image_height: int
    processing_time_ms: float


class CaptionResponseDTO(BaseModel):
    """DTO for image captioning response."""
    task: str = "caption_image"
    model: str
    caption: str
    processing_time_ms: float


class OCRResult(BaseModel):
    """OCR result for a single text block."""
    text: str
    confidence: float
    bbox: Optional[List[List[float]]] = None


class OCRResponseDTO(BaseModel):
    """DTO for OCR response."""
    task: str = "extract_text"
    model: str
    results: List[OCRResult]
    full_text: str
    processing_time_ms: float


class AnalyzeImageRequestDTO(BaseModel):
    """DTO for combined image analysis request."""
    task: TaskType = TaskType.CAPTION_IMAGE


class AnalyzeImageResponseDTO(BaseModel):
    """DTO for combined image analysis response."""
    caption: Optional[dict] = None
    detections: Optional[dict] = None
    ocr: Optional[dict] = None
