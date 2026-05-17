"""Device selection logic."""
from typing import Literal

import torch


def get_device(config: str = "auto") -> Literal["cuda", "mps", "cpu"]:
    """Select appropriate compute device."""
    if config == "auto":
        if torch.cuda.is_available():
            return "cuda"
        elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
            return "mps"
        return "cpu"
    return config


def get_device_info() -> dict:
    """Get device information for health check."""
    return {
        "device": get_device(),
        "cuda_available": torch.cuda.is_available(),
        "mps_available": hasattr(torch.backends, "mps") and torch.backends.mps.is_available(),
        "cuda_device_count": torch.cuda.device_count() if torch.cuda.is_available() else 0,
    }
