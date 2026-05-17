"""Image generation DTOs for application layer."""

from typing import Optional, List
from pydantic import BaseModel, Field


class GenerateImageInputDTO(BaseModel):
    """Input DTO for image generation request.

    Used by the API layer to receive requests and pass to use case.
    """

    prompt: str = Field(..., min_length=1, max_length=4000, description="Text description for image generation")
    negative_prompt: Optional[str] = Field(
        default="blurry, ugly, distorted, low quality, watermark, text, signature",
        max_length=2000,
        description="Things to avoid in the generated image",
    )
    width: int = Field(default=1024, ge=256, le=2048, description="Image width in pixels")
    height: int = Field(default=1024, ge=256, le=2048, description="Image height in pixels")
    num_inference_steps: int = Field(default=30, ge=1, le=150, description="Number of denoising steps")
    guidance_scale: float = Field(default=7.5, ge=1.0, le=20.0, description="Prompt adherence strength")
    seed: Optional[int] = Field(default=None, description="Random seed for reproducibility")
    num_images: int = Field(default=1, ge=1, le=4, description="Number of images to generate")
    style_preset: Optional[str] = Field(default=None, description="Style preset for generation")


class GenerateImageOutputDTO(BaseModel):
    """Output DTO for image generation response.

    Returned by the use case after successful image generation.
    """

    images: List[str] = Field(..., description="Base64-encoded generated images")
    seed: int = Field(..., description="Seed used for generation")
    model: str = Field(..., description="Model used for generation")
    prompt: str = Field(..., description="Original prompt")
    inference_steps: int = Field(..., description="Number of steps used")
    guidance_scale: float = Field(..., description="Guidance scale used")
    width: int = Field(..., description="Image width")
    height: int = Field(..., description="Image height")
    processing_time_ms: float = Field(..., description="Generation time in milliseconds")


class GenerateVariationInputDTO(BaseModel):
    """Input DTO for image variation request."""

    image: str = Field(..., description="Base64-encoded source image")
    prompt: str = Field(..., min_length=1, max_length=4000, description="Text description guiding the variation")
    strength: float = Field(default=0.5, ge=0.0, le=1.0, description="How much to change the original")
    num_inference_steps: int = Field(default=30, ge=1, le=150, description="Number of denoising steps")
    guidance_scale: float = Field(default=7.5, ge=1.0, le=20.0, description="Prompt adherence strength")
    seed: Optional[int] = Field(default=None, description="Random seed for reproducibility")
    num_images: int = Field(default=1, ge=1, le=4, description="Number of variations to generate")


class GenerateVariationOutputDTO(BaseModel):
    """Output DTO for image variation response."""

    images: List[str] = Field(..., description="Base64-encoded generated variations")
    seed: int = Field(..., description="Seed used for generation")
    prompt: str = Field(..., description="Original prompt")
    strength: float = Field(..., description="Variation strength used")
    inference_steps: int = Field(..., description="Number of steps used")
    processing_time_ms: float = Field(..., description="Generation time in milliseconds")


class UpscaleImageInputDTO(BaseModel):
    """Input DTO for image upscale request."""

    image: str = Field(..., description="Base64-encoded image to upscale")
    scale: int = Field(default=2, ge=2, le=4, description="Upscaling factor")
    prompt: Optional[str] = Field(default=None, max_length=1000, description="Optional guidance prompt")


class UpscaleImageOutputDTO(BaseModel):
    """Output DTO for image upscale response."""

    image: str = Field(..., description="Base64-encoded upscaled image")
    scale: int = Field(..., description="Upscaling factor applied")
    original_width: int = Field(..., description="Original image width")
    original_height: int = Field(..., description="Original image height")
    new_width: int = Field(..., description="Upscaled image width")
    new_height: int = Field(..., description="Upscaled image height")
    processing_time_ms: float = Field(..., description="Processing time in milliseconds")


class ModelInfoDTO(BaseModel):
    """DTO for model information."""

    model_id: str
    model_type: str
    capabilities: List[str]
    max_dimensions: tuple[int, int]
    recommended_steps: tuple[int, int]
    vram_required_gb: float
    supports_attention_slicing: bool
    supports_vae_slicing: bool


class ListModelsOutputDTO(BaseModel):
    """Output DTO for available models response."""

    models: List[ModelInfoDTO]
    default_model: str
