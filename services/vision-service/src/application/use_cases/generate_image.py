"""Generate image use case (application layer).

This use case orchestrates image generation by delegating to
the image generation service (infrastructure layer).
"""

from typing import Optional
import uuid
import time

from ...domain.services.image_generation_protocol import IImageGenerationService
from ..dtos.image_gen_dtos import (
    GenerateImageInputDTO,
    GenerateImageOutputDTO,
    GenerateVariationInputDTO,
    GenerateVariationOutputDTO,
    UpscaleImageInputDTO,
    UpscaleImageOutputDTO,
    ListModelsOutputDTO,
)


class GenerateImageUseCase:
    """Application use case for text-to-image generation.

    This use case handles the business logic for image generation,
    including parameter validation and response formatting.

    Architecture:
        API -> GenerateImageUseCase -> IImageGenerationService (implementation)
        (api)       (application)              (infrastructure)

    The use case is responsible for:
    - Input validation (business rules)
    - Response formatting
    - Timing and metrics
    - Delegating to infrastructure for actual generation
    """

    def __init__(self, image_service: IImageGenerationService):
        """Initialize the use case with an image generation service.

        Args:
            image_service: Implementation of IImageGenerationService protocol.
        """
        self._service = image_service

    async def execute(self, input_dto: GenerateImageInputDTO) -> GenerateImageOutputDTO:
        """Execute image generation.

        Args:
            input_dto: Input data transfer object with generation parameters.

        Returns:
            Output data transfer object with generated images and metadata.

        Raises:
            ValueError: If prompt is empty or parameters are invalid.
        """
        start_time = time.time()

        if not input_dto.prompt.strip():
            raise ValueError("Prompt cannot be empty")

        seed = input_dto.seed if input_dto.seed is not None else uuid.uuid4().time_low

        images = await self._service.generate(
            prompt=input_dto.prompt,
            negative_prompt=input_dto.negative_prompt,
            width=input_dto.width,
            height=input_dto.height,
            num_inference_steps=input_dto.num_inference_steps,
            guidance_scale=input_dto.guidance_scale,
            seed=seed,
            num_images=input_dto.num_images,
            style_preset=input_dto.style_preset,
        )

        processing_time_ms = (time.time() - start_time) * 1000

        return GenerateImageOutputDTO(
            images=images,
            seed=seed,
            model="stabilityai/stable-diffusion-2-1",
            prompt=input_dto.prompt,
            inference_steps=input_dto.num_inference_steps,
            guidance_scale=input_dto.guidance_scale,
            width=input_dto.width,
            height=input_dto.height,
            processing_time_ms=processing_time_ms,
        )


class GenerateVariationUseCase:
    """Application use case for generating image variations.

    Handles the business logic for creating variations of existing images.
    """

    def __init__(self, image_service: IImageGenerationService):
        """Initialize the use case with an image generation service."""
        self._service = image_service

    async def execute(
        self, input_dto: GenerateVariationInputDTO
    ) -> GenerateVariationOutputDTO:
        """Execute image variation generation.

        Args:
            input_dto: Input data transfer object with variation parameters.

        Returns:
            Output data transfer object with generated variations.

        Raises:
            ValueError: If prompt is empty or parameters are invalid.
        """
        start_time = time.time()

        if not input_dto.prompt.strip():
            raise ValueError("Prompt cannot be empty")

        seed = input_dto.seed if input_dto.seed is not None else uuid.uuid4().time_low

        images = await self._service.generate_variation(
            image=input_dto.image,
            prompt=input_dto.prompt,
            strength=input_dto.strength,
            num_inference_steps=input_dto.num_inference_steps,
            guidance_scale=input_dto.guidance_scale,
            seed=seed,
            num_images=input_dto.num_images,
        )

        processing_time_ms = (time.time() - start_time) * 1000

        return GenerateVariationOutputDTO(
            images=images,
            seed=seed,
            prompt=input_dto.prompt,
            strength=input_dto.strength,
            inference_steps=input_dto.num_inference_steps,
            processing_time_ms=processing_time_ms,
        )


class UpscaleImageUseCase:
    """Application use case for image upscaling.

    Handles the business logic for AI-powered image upscaling.
    """

    def __init__(self, image_service: IImageGenerationService):
        """Initialize the use case with an image generation service."""
        self._service = image_service

    async def execute(self, input_dto: UpscaleImageInputDTO) -> UpscaleImageOutputDTO:
        """Execute image upscaling.

        Args:
            input_dto: Input data transfer object with upscale parameters.

        Returns:
            Output data transfer object with upscaled image.

        Raises:
            ValueError: If scale is not 2 or 4.
        """
        from PIL import Image
        import base64
        import io

        start_time = time.time()

        if input_dto.scale not in (2, 4):
            raise ValueError("Scale must be 2 or 4")

        # Decode image to get original dimensions
        try:
            img_data = base64.b64decode(input_dto.image)
            original_img = Image.open(io.BytesIO(img_data))
            original_width, original_height = original_img.size
        except Exception as e:
            raise ValueError(f"Invalid base64 image: {e}")

        upscaled_b64 = await self._service.upscale(
            image=input_dto.image,
            scale=input_dto.scale,
            prompt=input_dto.prompt,
        )

        # Decode upscaled image to get new dimensions
        upscaled_data = base64.b64decode(upscaled_b64)
        upscaled_img = Image.open(io.BytesIO(upscaled_data))
        new_width, new_height = upscaled_img.size

        processing_time_ms = (time.time() - start_time) * 1000

        return UpscaleImageOutputDTO(
            image=upscaled_b64,
            scale=input_dto.scale,
            original_width=original_width,
            original_height=original_height,
            new_width=new_width,
            new_height=new_height,
            processing_time_ms=processing_time_ms,
        )


class ListModelsUseCase:
    """Application use case for listing available models."""

    def __init__(self, image_service: IImageGenerationService):
        """Initialize the use case with an image generation service."""
        self._service = image_service

    def execute(self) -> ListModelsOutputDTO:
        """Get available image generation models.

        Returns:
            Output DTO with list of available models.
        """
        models = self._service.get_available_models()
        return ListModelsOutputDTO(
            models=models,
            default_model="stabilityai/stable-diffusion-2-1",
        )
