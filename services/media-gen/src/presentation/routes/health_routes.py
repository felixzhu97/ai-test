"""Health Check Routes."""
from fastapi import APIRouter, Depends

from domain.repositories.model_cache_repository import ModelCacheRepository
from infrastructure.config.device_selector import get_device_info
from .image_routes import get_model_cache

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check(model_cache: ModelCacheRepository = Depends(get_model_cache)):
    """Health check endpoint."""
    device_info = get_device_info()
    model_name = getattr(model_cache, "model_name", "unknown")
    
    return {
        "status": "ok",
        "model": model_name,
        "device": device_info["device"],
        "cuda_available": device_info["cuda_available"],
        "mps_available": device_info["mps_available"],
        "cuda_device_count": device_info["cuda_device_count"],
        "pipeline_loaded": model_cache.is_loaded(),
    }


@router.post("/cache/clear")
async def clear_cache(model_cache: ModelCacheRepository = Depends(get_model_cache)):
    """Clear the model cache to free memory."""
    model_cache.clear()
    return {"status": "ok", "message": "Cache cleared successfully"}
