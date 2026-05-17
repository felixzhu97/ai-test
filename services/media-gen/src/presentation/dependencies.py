"""Dependency injection configuration."""
from functools import lru_cache


@lru_cache
def get_container():
    """Get dependency container (singleton).
    
    Returns a dictionary with all singleton dependencies.
    """
    from infrastructure.config.huggingface_config import configure_huggingface
    configure_huggingface()
    
    import os
    from infrastructure.adapters.stable_diffusion_adapter import StableDiffusionAdapter
    from infrastructure.adapters.image_encoder_adapter import ImageEncoderAdapter
    from infrastructure.config.device_selector import get_device
    
    device = get_device()
    
    return {
        "model_cache": StableDiffusionAdapter(
            model_name=os.getenv("SD_MODEL", "runwayml/stable-diffusion-v1-5"),
            device=device,
            hf_token=os.getenv("HF_TOKEN"),
        ),
        "image_encoder": ImageEncoderAdapter(),
    }


def get_model_cache():
    """Get model cache repository singleton."""
    container = get_container()
    return container["model_cache"]


def get_image_encoder():
    """Get image encoder adapter singleton."""
    container = get_container()
    return container["image_encoder"]
