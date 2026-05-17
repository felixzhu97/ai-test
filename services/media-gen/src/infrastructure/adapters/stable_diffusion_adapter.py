"""Stable Diffusion Pipeline Adapter - Implements ModelCacheRepository."""
from __future__ import annotations

import time
from typing import Any, Optional

import torch
from loguru import logger

from domain.repositories.model_cache_repository import ModelCacheRepository


class StableDiffusionAdapter(ModelCacheRepository):
    """Adapter for Stable Diffusion pipeline with caching."""

    def __init__(
        self,
        model_name: str,
        device: str,
        hf_token: Optional[str] = None,
        torch_dtype: Optional[torch.dtype] = None,
    ):
        self._model_name = model_name
        self._device = device
        self._hf_token = hf_token
        self._torch_dtype = torch_dtype
        self._pipeline: Optional[Any] = None

    @property
    def model_name(self) -> str:
        return self._model_name

    @property
    def device(self) -> str:
        return self._device

    def get_pipeline(self) -> Any:
        """Get or lazy-load the Stable Diffusion pipeline."""
        if self._pipeline is None:
            self._load_pipeline()
        return self._pipeline

    def is_loaded(self) -> bool:
        return self._pipeline is not None

    def clear(self) -> None:
        """Clear the cached pipeline and free memory."""
        if self._pipeline is not None:
            del self._pipeline
            self._pipeline = None

        if torch.cuda.is_available():
            torch.cuda.empty_cache()

        logger.info("Pipeline cache cleared")

    def load(self, model_id: str) -> Any:
        """Load a pipeline into cache (delegates to lazy loading)."""
        return self.get_pipeline()

    def _load_pipeline(self) -> None:
        """Load the Stable Diffusion pipeline."""
        from diffusers import StableDiffusionPipeline

        logger.info(f"Loading SD model '{self._model_name}' on device: {self._device}")

        start_time = time.time()

        load_kwargs = {
            "torch_dtype": self._torch_dtype or (torch.float16 if self._device == "cuda" else torch.float32),
            "safety_checker": None,
        }

        if self._hf_token:
            load_kwargs["use_auth_token"] = self._hf_token

        self._pipeline = StableDiffusionPipeline.from_pretrained(
            self._model_name,
            **load_kwargs,
        )
        self._pipeline = self._pipeline.to(self._device)

        if hasattr(self._pipeline, "enable_attention_slicing"):
            self._pipeline.enable_attention_slicing()

        elapsed = time.time() - start_time
        logger.info(f"Model loaded in {elapsed:.1f}s")
