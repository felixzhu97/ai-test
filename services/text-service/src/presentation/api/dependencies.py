"""FastAPI Dependency Injection providers."""

from typing import Optional
from fastapi import Depends

from src.domain import SessionRepository
from src.infrastructure import (
    LangChainLLMGateway,
    ConfigPort,
    PydanticConfigAdapter,
)
from src.infrastructure.repositories import InMemorySessionRepository
from src.application import ChatUseCase, CompletionUseCase
from src.core.config import get_settings


# Global instances (singletons for the application)
_session_repository: Optional[InMemorySessionRepository] = None
_llm_gateway: Optional[LangChainLLMGateway] = None


def get_session_repository() -> InMemorySessionRepository:
    """Get singleton session repository instance."""
    global _session_repository
    if _session_repository is None:
        _session_repository = InMemorySessionRepository()
    return _session_repository


def get_llm_gateway() -> LangChainLLMGateway:
    """Get singleton LLM gateway instance."""
    global _llm_gateway
    if _llm_gateway is None:
        settings = get_settings()
        config = PydanticConfigAdapter(settings)
        _llm_gateway = LangChainLLMGateway(config)
    return _llm_gateway


def get_chat_use_case(
    session_repo: InMemorySessionRepository = Depends(get_session_repository),
    llm_gateway: LangChainLLMGateway = Depends(get_llm_gateway),
) -> ChatUseCase:
    """Get ChatUseCase with injected dependencies."""
    return ChatUseCase(
        session_repository=session_repo,
        llm_gateway=llm_gateway,
    )


def get_completion_use_case(
    llm_gateway: LangChainLLMGateway = Depends(get_llm_gateway),
) -> CompletionUseCase:
    """Get CompletionUseCase with injected dependencies."""
    return CompletionUseCase(llm_gateway=llm_gateway)


def reset_llm_gateway() -> None:
    """Reset LLM gateway singleton (for testing)."""
    global _llm_gateway
    if _llm_gateway is not None:
        _llm_gateway.reset()
        _llm_gateway = None


def clear_session_repository() -> None:
    """Clear session repository (for testing)."""
    global _session_repository
    if _session_repository is not None:
        _session_repository.clear()
