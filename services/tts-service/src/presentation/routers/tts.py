"""TTS API endpoints.

This module contains the API routes for the TTS service.
Routes delegate to the application layer for business logic.
"""

from typing import Optional, List
from fastapi import APIRouter, HTTPException, Query, Depends
from fastapi.responses import StreamingResponse, JSONResponse
from loguru import logger

from ...application.dtos import (
    SynthesizeRequestDTO,
    StreamRequestDTO,
    VoiceDTO,
    ProviderDTO,
    HealthResponseDTO,
    OutputFormatDTO,
)
from ...application import TTSApplicationService
from .dependencies import get_tts_application_service, get_config_adapter

router = APIRouter(prefix="/tts", tags=["TTS"])


@router.post(
    "/synthesize",
    summary="Synthesize speech",
    description="Convert text to speech and return audio file",
    responses={
        200: {"content": {"audio/mpeg": {}, "audio/wav": {}, "audio/ogg": {}}},
        400: {"model": dict},
        503: {"model": dict},
    },
)
async def synthesize(
    request: SynthesizeRequestDTO,
    service: TTSApplicationService = Depends(get_tts_application_service),
):
    """Synthesize text to speech.
    
    Args:
        request: Synthesis parameters including text, voice, and audio settings.
        service: Injected application service.
    
    Returns:
        Audio file in the requested format.
    """
    try:
        logger.debug(f"Synthesizing text: {request.text[:50]}... with voice: {request.voice}")
        
        # Call application service
        response = await service.synthesize_speech(request)
        
        # Determine media type
        media_types = {
            OutputFormatDTO.MP3: "audio/mpeg",
            OutputFormatDTO.WAV: "audio/wav",
            OutputFormatDTO.OGG: "audio/ogg",
            OutputFormatDTO.FLAC: "audio/flac",
        }
        media_type = media_types.get(request.output_format, "audio/mpeg")
        
        return StreamingResponse(
            iter([response.audio_data]),
            media_type=media_type,
            headers={
                "Content-Disposition": f'attachment; filename="{response.filename}"',
                "Content-Length": str(response.size_bytes),
            }
        )
        
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        logger.error(f"Synthesis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/stream",
    summary="Stream speech synthesis",
    description="Stream synthesized speech in real-time",
    responses={
        200: {"content": {"audio/mpeg": {}, "audio/wav": {}, "audio/ogg": {}}},
        400: {"model": dict},
        503: {"model": dict},
    },
)
async def stream_synthesize(
    request: StreamRequestDTO,
    service: TTSApplicationService = Depends(get_tts_application_service),
):
    """Stream synthesized speech in real-time.
    
    Args:
        request: Stream parameters.
        service: Injected application service.
    
    Returns:
        Streaming audio chunks.
    """
    try:
        logger.debug(f"Streaming text: {request.text[:50]}...")
        
        # Determine media type
        media_types = {
            OutputFormatDTO.MP3: "audio/mpeg",
            OutputFormatDTO.WAV: "audio/wav",
            OutputFormatDTO.OGG: "audio/ogg",
            OutputFormatDTO.FLAC: "audio/flac",
        }
        media_type = media_types.get(request.output_format, "audio/mpeg")
        
        return StreamingResponse(
            service.stream_speech(request),
            media_type=media_type,
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Transfer-Encoding": "chunked",
            }
        )
        
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        logger.error(f"Streaming synthesis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/voices",
    summary="List voices",
    description="Get list of available voices for the current provider",
    response_model=List[VoiceDTO],
)
async def list_voices(
    language: Optional[str] = Query(None, description="Filter by language code"),
    service: TTSApplicationService = Depends(get_tts_application_service),
):
    """List available voices.
    
    Args:
        language: Optional language filter.
        service: Injected application service.
    
    Returns:
        List of available voices.
    """
    try:
        voices = await service.list_voices(language=language)
        return voices
    except Exception as e:
        logger.error(f"Failed to list voices: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/providers",
    summary="List providers",
    description="Get information about available TTS providers",
    response_model=List[ProviderDTO],
)
async def list_providers(
    service: TTSApplicationService = Depends(get_tts_application_service),
):
    """List all available TTS providers.
    
    Args:
        service: Injected application service.
    
    Returns:
        List of provider information.
    """
    try:
        providers = await service.get_providers()
        return providers
    except Exception as e:
        logger.error(f"Failed to list providers: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/provider",
    summary="Get current provider",
    description="Get information about the currently active TTS provider",
    response_model=ProviderDTO,
)
async def get_provider_info(
    service: TTSApplicationService = Depends(get_tts_application_service),
):
    """Get current provider information.
    
    Args:
        service: Injected application service.
    
    Returns:
        Current provider information.
    """
    try:
        provider = await service.get_current_provider()
        return provider
    except Exception as e:
        logger.error(f"Failed to get provider info: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/health",
    summary="Health check",
    description="Check TTS service health status",
    response_model=HealthResponseDTO,
)
async def health_check(
    service: TTSApplicationService = Depends(get_tts_application_service),
):
    """Check TTS service health.
    
    Args:
        service: Injected application service.
    
    Returns:
        Health status information.
    """
    try:
        health = await service.get_health()
        return health
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return HealthResponseDTO(
            status="unhealthy",
            provider="unknown",
            provider_status="error",
            version="0.1.0",
            components={"error": str(e)},
        )
