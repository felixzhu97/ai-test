"""API routes package."""

from fastapi import APIRouter

from .chat import router as chat_router
from .documents import router as documents_router

api_router = APIRouter()

api_router.include_router(chat_router)
api_router.include_router(documents_router)

__all__ = ["api_router"]
