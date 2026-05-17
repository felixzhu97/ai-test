"""API routes for Text-to-Text service - Refactored with Clean Architecture."""

import json
import uuid
import os
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from loguru import logger

from src.application import ChatUseCase, CompletionUseCase
from src.application.dto import (
    ChatMessageDTO,
    ChatRequestDTO,
    CompletionRequestDTO,
)
from src.presentation.api.dependencies import (
    get_chat_use_case,
    get_completion_use_case,
    get_session_repository,
    get_llm_gateway,
    reset_llm_gateway,
)
from src.infrastructure import verify_api_key
from .schemas import (
    Message,
    CompletionRequest,
    CompletionResponse,
    ChatRequest,
    ChatResponse,
    ModelInfo,
    ProviderInfo,
    HealthResponse,
)


router = APIRouter(prefix="/api/text", tags=["text-to-text"])

ENABLE_AUTH = os.getenv("ENABLE_API_AUTH", "false").lower() in ("true", "1", "yes")


@router.get("/health", response_model=HealthResponse)
async def health_check(
    llm_gateway = Depends(get_llm_gateway),
):
    """Health check endpoint."""
    return HealthResponse(
        status="ok",
        provider=llm_gateway.default_provider,
        model=llm_gateway.default_model,
        version="0.2.0",
    )


@router.get("/providers", response_model=list[ProviderInfo])
async def list_providers(
    api_key: str = Depends(verify_api_key) if ENABLE_AUTH else None,
):
    """List all available LLM providers and their models."""
    from src.core.config import get_settings
    settings = get_settings()
    
    return [
        ProviderInfo(
            name="openai",
            display_name="OpenAI",
            models=settings.OPENAI_MODELS.split(","),
            status="available" if settings.OPENAI_API_KEY else "configured",
        ),
        ProviderInfo(
            name="anthropic",
            display_name="Anthropic Claude",
            models=settings.ANTHROPIC_MODELS.split(","),
            status="available" if settings.ANTHROPIC_API_KEY else "configured",
        ),
        ProviderInfo(
            name="ollama",
            display_name="Ollama (Local)",
            models=settings.OLLAMA_MODELS.split(","),
            status="available",
        ),
    ]


@router.get("/models", response_model=list[ModelInfo])
async def list_models(
    provider: Optional[str] = None,
    api_key: str = Depends(verify_api_key) if ENABLE_AUTH else None,
):
    """List available models, optionally filtered by provider."""
    from src.core.config import get_settings
    settings = get_settings()
    
    models = []
    
    if provider is None or provider == "openai":
        for model_name in settings.OPENAI_MODELS.split(","):
            models.append(ModelInfo(
                name=model_name.strip(),
                provider="openai",
                description=f"OpenAI {model_name.strip()}",
                max_tokens=128000 if "o" in model_name else 16385,
            ))
    
    if provider is None or provider == "anthropic":
        for model_name in settings.ANTHROPIC_MODELS.split(","):
            models.append(ModelInfo(
                name=model_name.strip(),
                provider="anthropic",
                description=f"Anthropic {model_name.strip()}",
                max_tokens=200000,
            ))
    
    if provider is None or provider == "ollama":
        for model_name in settings.OLLAMA_MODELS.split(","):
            models.append(ModelInfo(
                name=model_name.strip(),
                provider="ollama",
                description=f"Ollama {model_name.strip()} (Local)",
                max_tokens=None,
            ))
    
    return models


@router.post("/complete", response_model=CompletionResponse)
async def complete(
    request: CompletionRequest,
    use_case: CompletionUseCase = Depends(get_completion_use_case),
    api_key: str = Depends(verify_api_key) if ENABLE_AUTH else None,
):
    """Generate a text completion."""
    try:
        request_dto = CompletionRequestDTO(
            prompt=request.prompt,
            system_prompt=request.system_prompt,
            provider=request.provider,
            model=request.model,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
        )
        
        response_dto = use_case.execute(request_dto)
        
        return CompletionResponse(
            text=response_dto.text,
            provider=response_dto.provider,
            model=response_dto.model,
            usage=response_dto.usage,
            finish_reason=response_dto.finish_reason,
        )
        
    except Exception as e:
        logger.error(f"Completion error: {e}")
        raise HTTPException(status_code=500, detail=f"Completion failed: {str(e)}")


@router.post("/complete/stream")
async def complete_stream(
    request: CompletionRequest,
    use_case: CompletionUseCase = Depends(get_completion_use_case),
    api_key: str = Depends(verify_api_key) if ENABLE_AUTH else None,
):
    """Stream a text completion."""
    try:
        request_dto = CompletionRequestDTO(
            prompt=request.prompt,
            system_prompt=request.system_prompt,
            provider=request.provider,
            model=request.model,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
        )
        
        async def generate():
            try:
                yield f"event: meta\n"
                yield f"data: {json.dumps({'provider': use_case._llm.default_provider, 'model': use_case._llm.default_model})}\n\n"
                
                for token in use_case.execute_stream(request_dto):
                    yield f"data: {json.dumps({'token': token})}\n\n"
                
                yield f"event: done\n"
                yield f"data: {json.dumps({'finish_reason': 'stop'})}\n\n"
                
            except Exception as e:
                logger.error(f"Stream error: {e}")
                yield f"event: error\n"
                yield f"data: {json.dumps({'error': str(e)})}\n\n"
        
        return StreamingResponse(
            generate(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
            },
        )
        
    except Exception as e:
        logger.error(f"Stream setup error: {e}")
        raise HTTPException(status_code=500, detail=f"Stream failed: {str(e)}")


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    use_case: ChatUseCase = Depends(get_chat_use_case),
    api_key: str = Depends(verify_api_key) if ENABLE_AUTH else None,
):
    """Generate a chat completion."""
    try:
        messages = [ChatMessageDTO(role=msg.role, content=msg.content) for msg in request.messages]
        request_dto = ChatRequestDTO(
            messages=messages,
            system_prompt=request.system_prompt,
            provider=request.provider,
            model=request.model,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            session_id=request.session_id,
        )
        
        response_dto = use_case.execute(request_dto)
        
        return ChatResponse(
            text=response_dto.text,
            provider=response_dto.provider,
            model=response_dto.model,
            session_id=response_dto.session_id,
            usage=response_dto.usage,
            finish_reason=response_dto.finish_reason,
        )
        
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")


@router.post("/chat/stream")
async def chat_stream(
    request: ChatRequest,
    use_case: ChatUseCase = Depends(get_chat_use_case),
    api_key: str = Depends(verify_api_key) if ENABLE_AUTH else None,
):
    """Stream a chat completion."""
    try:
        session_id = request.session_id or str(uuid.uuid4())
        
        messages = [ChatMessageDTO(role=msg.role, content=msg.content) for msg in request.messages]
        request_dto = ChatRequestDTO(
            messages=messages,
            system_prompt=request.system_prompt,
            provider=request.provider,
            model=request.model,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            session_id=session_id,
        )
        
        async def generate():
            try:
                full_response = []
                
                # Send metadata
                yield f"event: meta\n"
                yield f"data: {json.dumps({'session_id': session_id})}\n\n"
                
                # Stream tokens (execute_stream returns tuple)
                _, token_stream, _ = use_case.execute_stream(request_dto)
                for token in token_stream:
                    full_response.append(token)
                    yield f"data: {json.dumps({'token': token})}\n\n"
                
                # Finalize session with response (pass ChatMessageDTO list)
                use_case.finalize_session(
                    session_id=session_id,
                    messages=messages,  # Already ChatMessageDTO list
                    full_response="".join(full_response),
                )
                
                yield f"event: done\n"
                yield f"data: {json.dumps({'session_id': session_id, 'finish_reason': 'stop'})}\n\n"
                
            except Exception as e:
                logger.error(f"Stream error: {e}")
                yield f"event: error\n"
                yield f"data: {json.dumps({'error': str(e)})}\n\n"
        
        return StreamingResponse(
            generate(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Session-Id": session_id,
            },
        )
        
    except Exception as e:
        logger.error(f"Stream setup error: {e}")
        raise HTTPException(status_code=500, detail=f"Stream failed: {str(e)}")


@router.get("/session/{session_id}")
async def get_session(
    session_id: str,
    session_repo = Depends(get_session_repository),
    api_key: str = Depends(verify_api_key) if ENABLE_AUTH else None,
):
    """Get chat history for a session."""
    session = session_repo.get(session_id)
    if session is None:
        return {
            "session_id": session_id,
            "messages": [],
            "count": 0,
        }
    
    return {
        "session_id": session.id,
        "messages": [msg.to_dict() for msg in session.messages],
        "count": len(session.messages),
    }


@router.delete("/session/{session_id}")
async def clear_session(
    session_id: str,
    session_repo = Depends(get_session_repository),
    api_key: str = Depends(verify_api_key) if ENABLE_AUTH else None,
):
    """Clear chat history for a session."""
    if session_repo.delete(session_id):
        return {"status": "success", "message": f"Session {session_id} cleared"}
    return {"status": "not_found", "message": "Session not found"}


@router.post("/reset")
async def reset_llm(
    api_key: str = Depends(verify_api_key) if ENABLE_AUTH else None,
):
    """Reset the cached LLM instance (for model switching)."""
    reset_llm_gateway()
    return {"status": "success", "message": "LLM cache reset"}
