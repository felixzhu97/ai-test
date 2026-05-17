"""Image Encoder Adapter - Implements ImageEncoderPort."""
import base64

from domain.entities.generated_image import GeneratedImage
from domain.ports.image_encoder_port import ImageEncoderPort


class ImageEncoderAdapter(ImageEncoderPort):
    """Adapter for encoding images to base64."""

    def to_base64(self, image: GeneratedImage) -> str:
        """Encode image to base64 string."""
        return base64.b64encode(image.raw_bytes).decode("utf-8")

    def from_base64(self, b64_string: str) -> bytes:
        """Decode base64 string to bytes."""
        return base64.b64decode(b64_string)
