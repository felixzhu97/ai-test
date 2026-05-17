"""Image Generation DTOs - Data transfer objects for API layer."""
from pydantic import BaseModel, Field
from typing import Optional


class GenerationRequestDTO(BaseModel):
    """DTO for image generation request."""
    prompt: str = Field(..., min_length=1, max_length=1000)
    negative_prompt: str = Field(
        default="blurry, ugly, distorted, low quality, watermark, text, signature",
        max_length=500
    )
    width: int = Field(default=512, ge=256, le=1024)
    height: int = Field(default=512, ge=256, le=1024)
    num_inference_steps: int = Field(default=25, ge=1, le=100)
    guidance_scale: float = Field(default=7.5, ge=1.0, le=20.0)
    seed: Optional[int] = Field(default=None, ge=0)
    num_images: int = Field(default=1, ge=1, le=4)


class GenerationResponseDTO(BaseModel):
    """DTO for image generation response."""
    images: list[str]
    seed: int
    model: str
    prompt: str
    width: int
    height: int
    num_inference_steps: int
    guidance_scale: float
    processing_time_ms: float
