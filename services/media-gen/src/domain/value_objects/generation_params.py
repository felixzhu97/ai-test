"""GenerationParams Value Object - Validated parameters for image generation."""
from dataclasses import dataclass
from typing import Optional


MIN_STEPS = 1
MAX_STEPS = 150
DEFAULT_STEPS = 30

MIN_GUIDANCE_SCALE = 0.0
MAX_GUIDANCE_SCALE = 30.0
DEFAULT_GUIDANCE_SCALE = 7.5

MIN_WIDTH = 256
MAX_WIDTH = 2048
DEFAULT_WIDTH = 1024

MIN_HEIGHT = 256
MAX_HEIGHT = 2048
DEFAULT_HEIGHT = 1024

MIN_SEED = 0
MAX_SEED = 2**32 - 1
DEFAULT_SEED = 42


@dataclass(frozen=True)
class GenerationParams:
    """Value Object: Immutable and validated image generation parameters.
    
    All parameters are validated at construction time to ensure
    they fall within acceptable ranges.
    """
    prompt: str
    negative_prompt: str = ""
    num_inference_steps: int = DEFAULT_STEPS
    guidance_scale: float = DEFAULT_GUIDANCE_SCALE
    width: int = DEFAULT_WIDTH
    height: int = DEFAULT_HEIGHT
    seed: Optional[int] = None
    num_images: int = 1

    def __post_init__(self) -> None:
        if not self.prompt or not self.prompt.strip():
            raise ValueError("prompt cannot be empty")

        if not (MIN_STEPS <= self.num_inference_steps <= MAX_STEPS):
            raise ValueError(
                f"num_inference_steps must be between {MIN_STEPS} and {MAX_STEPS}, "
                f"got {self.num_inference_steps}"
            )

        if not (MIN_GUIDANCE_SCALE <= self.guidance_scale <= MAX_GUIDANCE_SCALE):
            raise ValueError(
                f"guidance_scale must be between {MIN_GUIDANCE_SCALE} and {MAX_GUIDANCE_SCALE}, "
                f"got {self.guidance_scale}"
            )

        if not (MIN_WIDTH <= self.width <= MAX_WIDTH):
            raise ValueError(
                f"width must be between {MIN_WIDTH} and {MAX_WIDTH}, got {self.width}"
            )

        if not (MIN_HEIGHT <= self.height <= MAX_HEIGHT):
            raise ValueError(
                f"height must be between {MIN_HEIGHT} and {MAX_HEIGHT}, got {self.height}"
            )

        if self.seed is not None and not (MIN_SEED <= self.seed <= MAX_SEED):
            raise ValueError(
                f"seed must be between {MIN_SEED} and {MAX_SEED}, got {self.seed}"
            )

        if self.num_images < 1:
            raise ValueError(f"num_images must be at least 1, got {self.num_images}")

    @property
    def is_random_seed(self) -> bool:
        """Check if a random seed should be used."""
        return self.seed is None
