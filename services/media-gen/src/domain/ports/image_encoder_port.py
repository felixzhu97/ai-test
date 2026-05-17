"""ImageEncoderPort - Port interface for image encoding/decoding."""
from abc import ABC, abstractmethod

from domain.entities.generated_image import GeneratedImage


class ImageEncoderPort(ABC):
    """Port interface for image encoding/decoding operations.
    
    This abstraction allows encoding images to various formats
    (base64, etc.) without coupling the domain to specific encoding libraries.
    """

    @abstractmethod
    def to_base64(self, image: GeneratedImage) -> str:
        """Encode a GeneratedImage to base64 string.
        
        Args:
            image: The generated image entity to encode.
            
        Returns:
            Base64-encoded string representation of the image.
        """
        pass

    @abstractmethod
    def from_base64(self, b64_string: str) -> bytes:
        """Decode a base64 string to raw bytes.
        
        Args:
            b64_string: Base64-encoded string.
            
        Returns:
            Raw bytes of the decoded image.
        """
        pass
