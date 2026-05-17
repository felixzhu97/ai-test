"""Image Generation API Routes."""
from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from loguru import logger

from application.use_cases.generate_image_use_case import GenerateImageUseCase
from application.dto.generation_dto import GenerationRequestDTO, GenerationResponseDTO
from domain.repositories.model_cache_repository import ModelCacheRepository
from domain.ports.image_encoder_port import ImageEncoderPort

if TYPE_CHECKING:
    from infrastructure.adapters.stable_diffusion_adapter import StableDiffusionAdapter
    from infrastructure.adapters.image_encoder_adapter import ImageEncoderAdapter


# Singleton instances for dependency injection
_model_cache_instance: ModelCacheRepository | None = None
_image_encoder_instance: ImageEncoderPort | None = None


def get_model_cache() -> ModelCacheRepository:
    """Get or create model cache repository singleton."""
    global _model_cache_instance
    
    if _model_cache_instance is None:
        import os
        from infrastructure.adapters.stable_diffusion_adapter import StableDiffusionAdapter
        from infrastructure.config.device_selector import get_device
        
        device = get_device()
        model_name = os.getenv("SD_MODEL", "runwayml/stable-diffusion-v1-5")
        hf_token = os.getenv("HF_TOKEN")
        
        _model_cache_instance = StableDiffusionAdapter(
            model_name=model_name,
            device=device,
            hf_token=hf_token,
        )
    
    return _model_cache_instance


def get_image_encoder() -> ImageEncoderPort:
    """Get image encoder adapter."""
    global _image_encoder_instance
    
    if _image_encoder_instance is None:
        from infrastructure.adapters.image_encoder_adapter import ImageEncoderAdapter
        _image_encoder_instance = ImageEncoderAdapter()
    
    return _image_encoder_instance


def get_generate_use_case(
    model_cache: ModelCacheRepository = Depends(get_model_cache),
    image_encoder: ImageEncoderPort = Depends(get_image_encoder),
) -> GenerateImageUseCase:
    """Factory for GenerateImageUseCase with dependencies."""
    return GenerateImageUseCase(
        model_cache=model_cache,
        image_encoder=image_encoder,
    )


router = APIRouter(prefix="/image", tags=["image"])


@router.post("/generate", response_model=GenerationResponseDTO)
async def generate_image(
    request: GenerationRequestDTO,
    background_tasks: BackgroundTasks,
    use_case: GenerateImageUseCase = Depends(get_generate_use_case),
):
    """
    Generate images from text prompt using Stable Diffusion.
    
    Returns base64-encoded PNG images.
    """
    try:
        logger.info(f"Generating image: '{request.prompt[:50]}...'")
        response = use_case.execute(request)
        logger.info(f"Generated {len(response.images)} image(s) in {response.processing_time_ms:.0f}ms")
        return response
    except Exception as e:
        logger.error(f"Image generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")
