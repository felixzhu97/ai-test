"""Image-related DTOs."""

from typing import Optional, List
from pydantic import BaseModel, Field


class ImageGenerationRequestDTO(BaseModel):
    """DTO for image generation request."""

    prompt: str = Field(..., min_length=1, max_length=4000)
    negative_prompt: Optional[str] = Field(
        default="blurry, ugly, distorted, low quality, watermark, text, signature",
        max_length=2000,
    )
    model: str = Field(default="sdxl")
    width: int = Field(default=1024, ge=256, le=2048)
    height: int = Field(default=1024, ge=256, le=2048)
    num_inference_steps: int = Field(default=30, ge=1, le=150)
    guidance_scale: float = Field(default=7.5, ge=1.0, le=20.0)
    seed: Optional[int] = None
    num_images: int = Field(default=1, ge=1, le=4)
    style_preset: Optional[str] = None


class ImageGenerationResponseDTO(BaseModel):
    """DTO for image generation response."""

    images: List[str]
    seed: int
    model: str
    prompt: str
    inference_steps: int
    guidance_scale: float
    width: int
    height: int
    processing_time_ms: float
    metadata: dict = {}


class ImageVariationRequest(BaseModel):
    """DTO for image variation request."""

    image: str = Field(..., description="Base64 encoded source image")
    prompt: str = Field(..., min_length=1, max_length=4000)
    strength: float = Field(default=0.5, ge=0.0, le=1.0)
    num_inference_steps: int = Field(default=30, ge=1, le=150)
    guidance_scale: float = Field(default=7.5, ge=1.0, le=20.0)
    seed: Optional[int] = None
    num_images: int = Field(default=1, ge=1, le=4)


class ImageUpscaleRequest(BaseModel):
    """DTO for image upscale request."""

    image: str = Field(..., description="Base64 encoded image to upscale")
    scale: int = Field(default=2, ge=2, le=4)
    prompt: Optional[str] = Field(default=None, max_length=1000)


class ModelInfo(BaseModel):
    """Model information."""

    model_id: str
    model_type: str
    capabilities: List[str]
    max_dimensions: tuple[int, int]
    recommended_steps: tuple[int, int]
    vram_required_gb: float
    supports_attention_slicing: bool
    supports_vae_slicing: bool


class AvailableModelsResponse(BaseModel):
    """DTO for available models response."""

    models: List[ModelInfo]
    default_model: str


# Backwards compatibility aliases
ImageGenRequest = ImageGenerationRequestDTO
ImageGenResponse = ImageGenerationResponseDTO
