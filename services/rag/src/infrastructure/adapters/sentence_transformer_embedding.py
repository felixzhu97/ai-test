"""SentenceTransformer embedding adapter - implements EmbeddingPort interface."""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional

import torch
from sentence_transformers import SentenceTransformer
from loguru import logger

from domain.ports.embedding import EmbeddingPort


def _get_settings():
    """Lazy import settings to avoid circular imports."""
    from config import get_settings
    return get_settings()


class SentenceTransformerEmbeddingAdapter(EmbeddingPort):
    """SentenceTransformer embedding adapter implementing EmbeddingPort interface."""

    def __init__(
        self,
        model_name: Optional[str] = None,
        device: Optional[str] = None,
    ) -> None:
        settings = _get_settings()
        self._model_name = model_name or settings.EMBEDDING_MODEL
        self.device = device or settings.EMBEDDING_DEVICE

        if not torch.cuda.is_available() and self.device == "cuda":
            logger.warning("CUDA not available, falling back to CPU")
            self.device = "cpu"

        self.model: Optional[SentenceTransformer] = None

    def _load_model(self) -> SentenceTransformer:
        """Load the sentence transformer model lazily."""
        if self.model is None:
            logger.info(f"Loading embedding model: {self._model_name} on {self.device}")
            self.model = SentenceTransformer(self._model_name, device=self.device)
            logger.info("Embedding model loaded successfully")
        return self.model

    @property
    def embedding_dim(self) -> int:
        """Get the embedding dimension."""
        model = self._load_model()
        return model.get_sentence_embedding_dimension()

    @property
    def model_name(self) -> str:
        """Get the model name."""
        return self._model_name

    def embed(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for a batch of texts (synchronous)."""
        model = self._load_model()
        embeddings = model.encode(
            texts,
            normalize_embeddings=True,
            convert_to_numpy=True,
            show_progress_bar=False,
        )
        return embeddings.tolist()

    def embed_query(self, text: str) -> list[float]:
        """Generate embedding for a single query text (synchronous)."""
        return self.embed([text])[0]

    async def async_embed(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for a batch of texts (asynchronous)."""
        return self.embed(texts)

    async def async_embed_query(self, text: str) -> list[float]:
        """Generate embedding for a single query text (asynchronous)."""
        return self.embed([text])[0]
