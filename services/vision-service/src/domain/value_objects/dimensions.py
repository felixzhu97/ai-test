"""Image dimensions value object."""

from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class Dimensions:
    """Immutable image dimensions.

    Enforces that dimensions are positive and divisible by 8 (for diffusion models).
    """

    width: int
    height: int

    MIN_DIMENSION = 256
    MAX_DIMENSION = 2048

    def __post_init__(self):
        if self.width < self.MIN_DIMENSION or self.height < self.MIN_DIMENSION:
            raise ValueError(f"Dimensions must be at least {self.MIN_DIMENSION}px")
        if self.width > self.MAX_DIMENSION or self.height > self.MAX_DIMENSION:
            raise ValueError(f"Dimensions cannot exceed {self.MAX_DIMENSION}px")
        if self.width % 8 != 0 or self.height % 8 != 0:
            raise ValueError("Dimensions must be divisible by 8")

    @property
    def aspect_ratio(self) -> float:
        return self.width / self.height

    def scale(self, factor: int) -> "Dimensions":
        """Return new dimensions scaled by factor."""
        return Dimensions(self.width * factor, self.height * factor)

    def to_tuple(self) -> Tuple[int, int]:
        return (self.width, self.height)
