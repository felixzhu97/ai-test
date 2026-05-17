"""Domain Layer - Pure Python business logic.

This layer contains:
- Entities: Core business objects (GeneratedImage)
- Value Objects: Immutable objects with validation (GenerationParams)
- Ports: Abstract interfaces for external dependencies (ModelCacheRepository)
- Errors: Domain-specific exception types
"""

from .entities.generated_image import GeneratedImage, ImageFormat
from .value_objects.generation_params import GenerationParams
from .repositories.model_cache_repository import ModelCacheRepository
from .ports.image_encoder_port import ImageEncoderPort
from .errors import (
    DomainError,
    ImageGenerationError,
    InvalidGenerationParamsError,
)

__all__ = [
    # Entities
    "GeneratedImage",
    "ImageFormat",
    # Value Objects
    "GenerationParams",
    # Ports
    "ModelCacheRepository",
    "ImageEncoderPort",
    # Errors
    "DomainError",
    "ImageGenerationError",
    "InvalidGenerationParamsError",
]
