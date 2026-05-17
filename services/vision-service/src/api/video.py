"""Video generation API endpoints."""

from fastapi import APIRouter, HTTPException, Depends
from ..application.dtos.video_dtos import (
    VideoGenerateRequest,
    VideoGenerateResponse,
    VideoTaskResponse,
    AdvancedVideoRequest,
)
from ..application.use_cases.generate_video import (
    GenerateVideoUseCase,
    GenerateVideoInput,
)
from ..application.use_cases.check_video_status import (
    CheckVideoStatusUseCase,
    CheckVideoStatusInput,
)
from ..domain.value_objects.video_config import AspectRatio as DomainAspectRatio, VideoQuality as DomainVideoQuality
from ..domain.entities.video_task import TaskNotFoundError
from ..core.dependencies import get_video_generation_service
from loguru import logger
from datetime import datetime

router = APIRouter(prefix="/video", tags=["Video Generation"])


def _dto_to_domain_aspect_ratio(dto_ratio) -> DomainAspectRatio:
    """Map DTO aspect ratio to domain aspect ratio."""
    mapping = {
        "16:9": DomainAspectRatio.RATIO_16_9,
        "9:16": DomainAspectRatio.RATIO_9_16,
        "1:1": DomainAspectRatio.RATIO_1_1,
        "4:3": DomainAspectRatio.RATIO_4_3,
    }
    return mapping.get(dto_ratio.value, DomainAspectRatio.RATIO_16_9)


def _dto_to_domain_quality(dto_quality) -> DomainVideoQuality:
    """Map DTO quality to domain quality."""
    mapping = {
        "standard": DomainVideoQuality.STANDARD,
        "high": DomainVideoQuality.HIGH,
    }
    return mapping.get(dto_quality.value, DomainVideoQuality.HIGH)


@router.post("/generate", response_model=VideoGenerateResponse)
async def generate_video(
    request: VideoGenerateRequest,
    service=Depends(get_video_generation_service)
):
    try:
        use_case = GenerateVideoUseCase(service)
        input_data = GenerateVideoInput(
            prompt=request.prompt,
            negative_prompt=request.negative_prompt,
            duration=request.duration,
            aspect_ratio=_dto_to_domain_aspect_ratio(request.aspect_ratio),
            fps=request.fps,
            quality=_dto_to_domain_quality(request.quality),
        )
        result = await use_case.execute(input_data)
        return VideoGenerateResponse(
            task_id=result.task_id,
            status=result.status,
            message=result.message,
            created_at=datetime.now().isoformat()
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Video generation error: {e}")
        raise HTTPException(status_code=500, detail=f"Video generation failed: {str(e)}")


@router.post("/generate/advanced", response_model=VideoGenerateResponse)
async def generate_video_advanced(
    request: AdvancedVideoRequest,
    service=Depends(get_video_generation_service)
):
    try:
        use_case = GenerateVideoUseCase(service)
        input_data = GenerateVideoInput(
            prompt=request.prompt,
            negative_prompt=request.negative_prompt,
            duration=request.duration,
            aspect_ratio=_dto_to_domain_aspect_ratio(request.aspect_ratio),
            fps=request.fps,
            quality=_dto_to_domain_quality(request.quality),
            seed=request.seed,
        )
        result = await use_case.execute(input_data)
        return VideoGenerateResponse(
            task_id=result.task_id,
            status=result.status,
            message=result.message,
            created_at=datetime.now().isoformat()
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Video generation error: {e}")
        raise HTTPException(status_code=500, detail=f"Video generation failed: {str(e)}")


@router.get("/status/{task_id}", response_model=VideoTaskResponse)
async def get_video_status(
    task_id: str,
    service=Depends(get_video_generation_service)
):
    try:
        use_case = CheckVideoStatusUseCase(service)
        input_data = CheckVideoStatusInput(task_id=task_id)
        result = await use_case.execute(input_data)
        return VideoTaskResponse(
            task_id=result.task_id,
            status=result.status,
            video_url=result.video_url,
            thumbnail_url=result.thumbnail_url,
            error=result.error,
            processing_time_seconds=result.processing_time_seconds,
        )
    except TaskNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Status check error: {e}")
        raise HTTPException(status_code=500, detail=f"Status check failed: {str(e)}")
