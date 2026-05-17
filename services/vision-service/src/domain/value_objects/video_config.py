"""Video configuration value object."""

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class AspectRatio(str, Enum):
    RATIO_16_9 = "16:9"
    RATIO_9_16 = "9:16"
    RATIO_1_1 = "1:1"
    RATIO_4_3 = "4:3"


class VideoQuality(str, Enum):
    STANDARD = "standard"
    HIGH = "high"


@dataclass(frozen=True)
class VideoConfig:
    """Immutable video generation configuration."""

    duration: int
    aspect_ratio: AspectRatio
    fps: int
    quality: VideoQuality
    negative_prompt: Optional[str] = None
    seed: Optional[int] = None

    def __post_init__(self):
        if not 5 <= self.duration <= 10:
            raise ValueError("Duration must be between 5 and 10 seconds")
        if not 24 <= self.fps <= 60:
            raise ValueError("FPS must be between 24 and 60")
