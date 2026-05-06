from sentence_transformers import SentenceTransformer
import torch
from loguru import logger
from typing import Optional
from ..config import get_settings


class EmbeddingModel:
    """Embedding model wrapper for text vectorization."""

    def __init__(
        self,
        model_name: Optional[str] = None,
        device: Optional[str] = None,
    ):
        settings = get_settings()
        self.model_name = model_name or settings.EMBEDDING_MODEL
        self.device = device or settings.EMBEDDING_DEVICE

        if not torch.cuda.is_available() and self.device == "cuda":
            logger.warning("CUDA not available, falling back to CPU")
            self.device = "cpu"

        logger.info(f"Loading embedding model: {self.model_name} on {self.device}")
        self.model = SentenceTransformer(self.model_name, device=self.device)
        logger.info("Embedding model loaded successfully")

    def embed(self, texts: list[str], normalize: bool = True) -> list[list[float]]:
        """Generate embeddings for a list of texts."""
        embeddings = self.model.encode(
            texts,
            normalize_embeddings=normalize,
            convert_to_numpy=True,
            show_progress_bar=False,
        )
        return embeddings.tolist()

    def embed_query(self, text: str) -> list[float]:
        """Generate embedding for a single query text."""
        embedding = self.model.encode(
            text,
            normalize_embeddings=True,
            convert_to_numpy=True,
        )
        return embedding.tolist()

    @property
    def dimension(self) -> int:
        """Get the embedding dimension."""
        return self.model.get_sentence_embedding_dimension()

    def __call__(self, texts: list[str]) -> list[list[float]]:
        """Allow using the model as a callable."""
        return self.embed(texts)


_embedding_instance: Optional[EmbeddingModel] = None


def get_embedding_model() -> EmbeddingModel:
    """Get or create the global embedding model instance."""
    global _embedding_instance
    if _embedding_instance is None:
        _embedding_instance = EmbeddingModel()
    return _embedding_instance


def reset_embedding_model():
    """Reset the global embedding model instance."""
    global _embedding_instance
    _embedding_instance = None
