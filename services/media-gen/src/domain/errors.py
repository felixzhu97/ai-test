"""Domain Errors - Core business rule violations."""
from typing import Optional


class DomainError(Exception):
    """Base exception for all domain errors."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)


class ImageGenerationError(DomainError):
    """Error raised when image generation fails.
    
    This includes pipeline errors, hardware failures,
    or any issues during the generation process.
    """

    def __init__(self, message: str, cause: Optional[Exception] = None) -> None:
        super().__init__(message)
        self.cause = cause


class InvalidGenerationParamsError(DomainError):
    """Error raised when generation parameters are invalid.
    
    This is thrown when the input parameters violate
    domain constraints or business rules.
    """

    def __init__(self, message: str) -> None:
        super().__init__(message)


class PipelineNotLoadedError(DomainError):
    """Error raised when attempting to generate without a loaded pipeline."""

    def __init__(self, message: str = "ML pipeline is not loaded") -> None:
        super().__init__(message)

