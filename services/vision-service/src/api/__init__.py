from .vision import router as vision_router
from .video import router as video_router
from .image_gen import router as image_gen_router

__all__ = ["vision_router", "video_router", "image_gen_router"]
