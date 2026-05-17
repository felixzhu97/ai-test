"""Infrastructure Adapters - Concrete implementations of domain ports."""

from .stable_diffusion_adapter import StableDiffusionAdapter
from .image_encoder_adapter import ImageEncoderAdapter

__all__ = [
    "StableDiffusionAdapter",
    "ImageEncoderAdapter",
]
