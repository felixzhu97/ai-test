"""Dependency injection container for Vision Service."""

from functools import lru_cache
from typing import Generator
import torch
from PIL import Image


class ModelContainer:
    """Container for managing model instances."""

    _yolo = None
    _blip = None
    _easyocr = None
    _generator = None

    @classmethod
    def get_yolo(cls):
        if cls._yolo is None:
            from ..models.yolo_detector import YOLODetector
            cls._yolo = YOLODetector()
        return cls._yolo

    @classmethod
    def get_blip(cls):
        if cls._blip is None:
            from ..models.blip_captioner import BLIPCaptioner
            cls._blip = BLIPCaptioner()
        return cls._blip

    @classmethod
    def get_easyocr(cls):
        if cls._easyocr is None:
            from ..models.easy_ocr import EasyOCRProcessor
            cls._easyocr = EasyOCRProcessor()
        return cls._easyocr

    @classmethod
    def get_generator(cls):
        if cls._generator is None:
            from ..models.text_to_image import get_generator
            cls._generator = get_generator()
        return cls._generator

    @classmethod
    def reset(cls):
        """Reset all model instances. Useful for testing."""
        cls._yolo = None
        cls._blip = None
        cls._easyocr = None
        cls._generator = None


def get_yolo():
    """FastAPI dependency for YOLO detector."""
    return ModelContainer.get_yolo()


def get_blip():
    """FastAPI dependency for BLIP captioner."""
    return ModelContainer.get_blip()


def get_easyocr():
    """FastAPI dependency for EasyOCR processor."""
    return ModelContainer.get_easyocr()


def get_generator():
    """FastAPI dependency for image generator."""
    return ModelContainer.get_generator()


def get_video_provider():
    """FastAPI dependency for video provider."""
    from ..providers import get_provider
    from ..core.config import get_settings
    settings = get_settings()

    api_key = ""
    api_secret = ""

    if settings.VIDEO_PROVIDER.value == "replicate":
        api_key = settings.REPLICATE_API_TOKEN
    elif settings.VIDEO_PROVIDER.value == "kling":
        api_key = settings.KLING_API_KEY
        api_secret = settings.KLING_API_SECRET
    elif settings.VIDEO_PROVIDER.value == "runway":
        api_key = settings.RUNWAY_API_KEY
    elif settings.VIDEO_PROVIDER.value == "pika":
        api_key = settings.PIKA_API_KEY
    elif settings.VIDEO_PROVIDER.value == "sora":
        api_key = settings.SORA_API_KEY

    return get_provider(
        provider_name=settings.VIDEO_PROVIDER.value,
        api_key=api_key,
        api_secret=api_secret
    )
