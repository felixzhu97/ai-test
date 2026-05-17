"""Image Generation Use Case."""
import io
import time
import uuid
from datetime import datetime

from domain.entities.generated_image import GeneratedImage
from domain.errors import ImageGenerationError
from domain.repositories.model_cache_repository import ModelCacheRepository
from domain.ports.image_encoder_port import ImageEncoderPort
from ..dto.generation_dto import GenerationRequestDTO, GenerationResponseDTO


class GenerateImageUseCase:
    """Use case for generating images from text prompts."""

    def __init__(
        self,
        model_cache: ModelCacheRepository,
        image_encoder: ImageEncoderPort,
    ):
        self._model_cache = model_cache
        self._encoder = image_encoder

    def execute(self, request: GenerationRequestDTO) -> GenerationResponseDTO:
        """Execute image generation."""
        start_time = time.time()

        # get_pipeline() handles lazy loading if not already loaded
        pipeline = self._model_cache.get_pipeline()

        seed = request.seed if request.seed is not None else self._generate_seed()

        try:
            result = pipeline(
                prompt=request.prompt,
                negative_prompt=request.negative_prompt,
                width=request.width,
                height=request.height,
                num_inference_steps=request.num_inference_steps,
                guidance_scale=request.guidance_scale,
                generator=self._create_generator(seed),
                num_images_per_prompt=request.num_images,
            )
        except Exception as e:
            raise ImageGenerationError(f"Image generation failed: {str(e)}", cause=e)

        images_b64 = []
        for img in result.images:
            generated = GeneratedImage(
                image_id=str(uuid.uuid4()),
                prompt=request.prompt,
                negative_prompt=request.negative_prompt,
                seed=seed,
                width=request.width,
                height=request.height,
                num_inference_steps=request.num_inference_steps,
                guidance_scale=request.guidance_scale,
                created_at=datetime.now(),
                raw_bytes=self._pil_to_bytes(img),
            )
            images_b64.append(self._encoder.to_base64(generated))

        processing_time = (time.time() - start_time) * 1000

        return GenerationResponseDTO(
            images=images_b64,
            seed=seed,
            model=getattr(self._model_cache, "model_name", "unknown"),
            prompt=request.prompt,
            width=request.width,
            height=request.height,
            num_inference_steps=request.num_inference_steps,
            guidance_scale=request.guidance_scale,
            processing_time_ms=processing_time,
        )

    def _generate_seed(self) -> int:
        import torch
        return torch.randint(0, 2**32 - 1, (1,)).item()

    def _create_generator(self, seed: int):
        import torch
        return torch.Generator(device=getattr(self._model_cache, "device", "cpu")).manual_seed(seed)

    def _pil_to_bytes(self, img) -> bytes:
        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        return buffered.getvalue()
