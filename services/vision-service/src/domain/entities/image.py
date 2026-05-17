"""Image generation entity."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List
from enum import Enum
import uuid


class ImageModel(str, Enum):
    SD3 = "sd3"
    SDXL = "sdxl"
    SD35_MEDIUM = "sd35_medium"
    SD35_LARGE = "sd35_large"


@dataclass
class ImageGeneration:
    """Image generation entity.

    Encapsulates the business rules for image generation,
    including validation and seed management.
    """

    prompt: str
    negative_prompt: str = "blurry, ugly, distorted, low quality, watermark, text, signature"
    model: ImageModel = ImageModel.SDXL
    width: int = 1024
    height: int = 1024
    num_inference_steps: int = 30
    guidance_scale: float = 7.5
    num_images: int = 1
    style_preset: Optional[str] = None
    seed: Optional[int] = field(default_factory=lambda: uuid.uuid4().time_low)

    generation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None

    def __post_init__(self):
        self._validate()

    def _validate(self) -> None:
        """Validate generation parameters."""
        if not self.prompt.strip():
            raise ValueError("Prompt cannot be empty")
        if self.width < 256 or self.height < 256:
            raise ValueError("Dimensions must be at least 256px")
        if self.width > 2048 or self.height > 2048:
            raise ValueError("Dimensions cannot exceed 2048px")
        if self.width % 8 != 0 or self.height % 8 != 0:
            raise ValueError("Dimensions must be divisible by 8")
        if not 1 <= self.num_inference_steps <= 150:
            raise ValueError("Inference steps must be between 1 and 150")
        if not 1.0 <= self.guidance_scale <= 20.0:
            raise ValueError("Guidance scale must be between 1.0 and 20.0")
        if not 1 <= self.num_images <= 4:
            raise ValueError("Number of images must be between 1 and 4")

    def mark_completed(self) -> None:
        """Mark generation as completed."""
        self.completed_at = datetime.now()

    @property
    def duration_ms(self) -> Optional[float]:
        """Calculate processing duration in milliseconds."""
        if self.completed_at:
            return (self.completed_at - self.created_at).total_seconds() * 1000
        return None
