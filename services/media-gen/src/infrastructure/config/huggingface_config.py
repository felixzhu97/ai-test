"""HuggingFace configuration."""
import os


def configure_huggingface() -> None:
    """Configure HF endpoint from environment (e.g., mirror)."""
    hf_endpoint = os.getenv("HF_ENDPOINT")
    if hf_endpoint:
        os.environ["HF_ENDPOINT"] = hf_endpoint
