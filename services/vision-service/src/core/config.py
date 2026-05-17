from enum import Enum
from pydantic_settings import BaseSettings
from functools import lru_cache


class VideoProvider(str, Enum):
    REPLICATE = "replicate"
    KLING = "kling"
    RUNWAY = "runway"
    PIKA = "pika"
    SORA = "sora"
    MOCK = "mock"


class Settings(BaseSettings):
    YOLO_MODEL: str = "yolo11n.pt"
    BLIP_MODEL: str = "Salesforce/blip-image-captioning-large"
    OCR_LANG: str = "ch"
    MAX_IMAGE_SIZE: int = 10 * 1024 * 1024
    DEVICE: str = "cuda"
    MODEL_CACHE_DIR: str = "./models"
    MAX_CONCURRENT_REQUESTS: int = 4
    HF_ENDPOINT: str = ""

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
