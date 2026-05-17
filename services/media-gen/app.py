"""Media Generation Service - Entry Point."""
import os
import sys

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from src.core.settings import get_settings
from src.infrastructure.config.huggingface_config import configure_huggingface
from src.presentation.routes.image_routes import router as image_router, get_model_cache
from src.presentation.routes.health_routes import router as health_router

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    logger.info("Starting Media Generation Service...")
    logger.info(f"Model: {settings.sd_model}")

    configure_huggingface()

    yield

    logger.info("Shutting down Media Generation Service...")


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    app = FastAPI(
        title="Media Generation Service",
        description="Text-to-Image generation using Stable Diffusion",
        version="0.2.0",
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # CORS middleware
    origins = [o.strip() for o in settings.cors_origins.split(",") if o.strip()]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
    )

    # Include routers
    app.include_router(image_router)
    app.include_router(health_router)

    # Root endpoint
    @app.get("/")
    async def root():
        return {
            "service": "Media Generation Service",
            "version": "0.2.0",
            "model": settings.sd_model,
            "endpoints": {
                "health": "/health",
                "generate": "/image/generate",
                "clear_cache": "/cache/clear",
                "docs": "/docs",
            }
        }

    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app:app",
        host=settings.host,
        port=settings.port,
        reload=False,
    )
