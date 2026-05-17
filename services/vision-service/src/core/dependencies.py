"""Dependency injection container for Vision Service."""

from typing import Optional, Protocol, runtime_checkable
import torch
from PIL import Image


@runtime_checkable
class ObjectDetector(Protocol):
    """Protocol for object detection models."""

    async def detect(
        self, image: Image.Image, conf_threshold: float = 0.25
    ) -> dict: ...


@runtime_checkable
class ImageCaptioner(Protocol):
    """Protocol for image captioning models."""

    async def caption(self, image: Image.Image) -> dict: ...


@runtime_checkable
class OCRProcessor(Protocol):
    """Protocol for OCR models."""

    async def extract_text(
        self, image: Image.Image, engine: str = "easyocr"
    ) -> dict: ...


@runtime_checkable
class ImageGenerator(Protocol):
    """Protocol for image generation models."""

    async def generate(self, prompt: str, **kwargs) -> dict: ...


# Module-level lazy-initialized singletons (replaces class variables in ModelContainer)
_yolo_instance: Optional[ObjectDetector] = None
_blip_instance: Optional[ImageCaptioner] = None
_easyocr_instance: Optional[OCRProcessor] = None
_generator_instance: Optional[ImageGenerator] = None


def _reset_instances() -> None:
    """Reset all model instances. Useful for testing."""
    global _yolo_instance, _blip_instance, _easyocr_instance, _generator_instance
    _yolo_instance = None
    _blip_instance = None
    _easyocr_instance = None
    _generator_instance = None


# FastAPI dependencies - standard dependency injection pattern
def get_yolo() -> ObjectDetector:
    """FastAPI dependency for YOLO detector with lazy initialization."""
    global _yolo_instance
    if _yolo_instance is None:
        from ..models.yolo_detector import YOLODetector
        _yolo_instance = YOLODetector()
    return _yolo_instance


def get_blip() -> ImageCaptioner:
    """FastAPI dependency for BLIP captioner with lazy initialization."""
    global _blip_instance
    if _blip_instance is None:
        from ..models.blip_captioner import BLIPCaptioner
        _blip_instance = BLIPCaptioner()
    return _blip_instance


def get_easyocr() -> OCRProcessor:
    """FastAPI dependency for EasyOCR processor with lazy initialization."""
    global _easyocr_instance
    if _easyocr_instance is None:
        from ..models.easy_ocr import EasyOCRProcessor
        _easyocr_instance = EasyOCRProcessor()
    return _easyocr_instance


def get_generator() -> ImageGenerator:
    """FastAPI dependency for image generator with lazy initialization."""
    global _generator_instance
    if _generator_instance is None:
        from ..models.text_to_image import get_generator as _get_gen
        _generator_instance = _get_gen()
    return _generator_instance


def get_video_provider():
    """FastAPI dependency for video provider."""
    from ..infrastructure.providers import get_provider
    return get_provider()


def get_video_generation_service():
    """FastAPI dependency for video generation service (infrastructure layer).

    This function creates a VideoGenerationServiceImpl instance
    with the configured video provider.
    """
    from ..infrastructure.services import VideoGenerationServiceImpl
    provider = get_video_provider()
    return VideoGenerationServiceImpl(provider)


# Image Generation Use Cases


def get_image_generation_service():
    """FastAPI dependency for image generation service (infrastructure layer).

    Returns an ImageGenerationServiceImpl instance that implements
    the IImageGenerationService protocol.
    """
    from ..infrastructure.services.image_generation_service_impl import (
        ImageGenerationServiceImpl,
    )

    return ImageGenerationServiceImpl()


def get_generate_image_use_case(
    image_service=None,
) -> "GenerateImageUseCase":
    """FastAPI dependency for generate image use case.

    Args:
        image_service: Optional IImageGenerationService instance.
                     If not provided, gets from get_image_generation_service().

    Returns:
        GenerateImageUseCase instance ready for use.
    """
    from ..application.use_cases.generate_image import GenerateImageUseCase

    if image_service is None:
        image_service = get_image_generation_service()
    return GenerateImageUseCase(image_service)


def get_generate_variation_use_case(
    image_service=None,
) -> "GenerateVariationUseCase":
    """FastAPI dependency for generate variation use case.

    Args:
        image_service: Optional IImageGenerationService instance.

    Returns:
        GenerateVariationUseCase instance ready for use.
    """
    from ..application.use_cases.generate_image import GenerateVariationUseCase

    if image_service is None:
        image_service = get_image_generation_service()
    return GenerateVariationUseCase(image_service)


def get_upscale_image_use_case(
    image_service=None,
) -> "UpscaleImageUseCase":
    """FastAPI dependency for upscale image use case.

    Args:
        image_service: Optional IImageGenerationService instance.

    Returns:
        UpscaleImageUseCase instance ready for use.
    """
    from ..application.use_cases.generate_image import UpscaleImageUseCase

    if image_service is None:
        image_service = get_image_generation_service()
    return UpscaleImageUseCase(image_service)


def get_list_models_use_case(
    image_service=None,
) -> "ListModelsUseCase":
    """FastAPI dependency for list models use case.

    Args:
        image_service: Optional IImageGenerationService instance.

    Returns:
        ListModelsUseCase instance ready for use.
    """
    from ..application.use_cases.generate_image import ListModelsUseCase

    if image_service is None:
        image_service = get_image_generation_service()
    return ListModelsUseCase(image_service)


# Backward compatibility - deprecated service locator pattern
class ModelContainer:
    """Deprecated: Use get_yolo(), get_blip(), get_easyocr(), get_generator() instead.

    This class is kept for backward compatibility during migration.
    It will be removed in a future version.
    """

    _yolo = None
    _blip = None
    _easyocr = None
    _generator = None

    @classmethod
    def get_yolo(cls):
        return get_yolo()

    @classmethod
    def get_blip(cls):
        return get_blip()

    @classmethod
    def get_easyocr(cls):
        return get_easyocr()

    @classmethod
    def get_generator(cls):
        return get_generator()

    @classmethod
    def reset(cls):
        """Reset all model instances. Useful for testing."""
        _reset_instances()


def get_analyze_image_use_case():
    """FastAPI dependency for analyze image use case."""
    from ..application.use_cases.analyze_image import AnalyzeImageUseCase
    detector = get_yolo()
    captioner = get_blip()
    ocr = get_easyocr()
    return AnalyzeImageUseCase(detector=detector, captioner=captioner, ocr=ocr)
