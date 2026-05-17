from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor

from ..application.dtos.image_dtos import (
    ImageGenRequest,
    ImageGenResponse,
    ImageVariationRequest,
    ImageUpscaleRequest,
    AvailableModelsResponse,
)
from ..core.dependencies import get_generator
from ..core.image_gen_config import get_image_gen_settings
from ..models.text_to_image import TextToImageGenerator

router = APIRouter(prefix="/image-gen", tags=["image-generation"])
logger = logging.getLogger(__name__)

_executor = ThreadPoolExecutor(max_workers=2)


@router.post("/generate", response_model=ImageGenResponse)
async def generate_image(
    request: ImageGenRequest,
    generator: TextToImageGenerator = Depends(get_generator)
):
    """Generate images from text prompt using Stable Diffusion."""
    if not request.prompt.strip():
        raise HTTPException(400, "Prompt cannot be empty")
    
    settings = get_image_gen_settings()
    
    if request.width > settings.MAX_IMAGE_SIZE or request.height > settings.MAX_IMAGE_SIZE:
        raise HTTPException(
            400, 
            f"Image dimensions cannot exceed {settings.MAX_IMAGE_SIZE}px"
        )
    
    if request.num_inference_steps > 150:
        raise HTTPException(400, "Maximum 150 inference steps allowed")

    try:
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            _executor,
            generator.generate,
            request
        )
        return result
    except Exception as e:
        logger.error(f"Image generation failed: {e}")
        raise HTTPException(500, f"Generation failed: {str(e)}")


@router.post("/variation", response_model=ImageGenResponse)
async def generate_variation(
    request: ImageVariationRequest,
    generator: TextToImageGenerator = Depends(get_generator)
):
    """Generate variations of an existing image."""
    if not request.prompt.strip():
        raise HTTPException(400, "Prompt cannot be empty")
    
    try:
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            _executor,
            generator.generate_variation,
            request
        )
        return result
    except Exception as e:
        logger.error(f"Variation generation failed: {e}")
        raise HTTPException(500, f"Variation failed: {str(e)}")


@router.post("/upscale", response_model=ImageGenResponse)
async def upscale_image(
    request: ImageUpscaleRequest,
    generator: TextToImageGenerator = Depends(get_generator)
):
    """Upscale an image using AI-powered upsampling."""
    if request.scale not in (2, 4):
        raise HTTPException(400, "Scale must be 2 or 4")

    try:
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            _executor,
            generator.upscale,
            request
        )
        return result
    except Exception as e:
        logger.error(f"Upscaling failed: {e}")
        raise HTTPException(500, f"Upscaling failed: {str(e)}")


@router.get("/models", response_model=AvailableModelsResponse)
async def list_models(
    generator: TextToImageGenerator = Depends(get_generator)
):
    """Get information about available image generation models."""
    return generator.get_available_models()


@router.post("/cache/clear")
async def clear_cache(
    generator: TextToImageGenerator = Depends(get_generator)
):
    """Clear the model cache to free GPU memory."""
    generator.clear_cache()
    return {"status": "ok", "message": "Cache cleared successfully"}


@router.get("/health")
async def health_check(
    generator: TextToImageGenerator = Depends(get_generator)
):
    """Check the status of the image generation service."""
    import torch
    
    return {
        "status": "ok",
        "device": generator.device,
        "cuda_available": torch.cuda.is_available(),
        "cuda_device_count": torch.cuda.device_count() if torch.cuda.is_available() else 0,
        "loaded_pipelines": list(generator._pipelines.keys()),
    }
