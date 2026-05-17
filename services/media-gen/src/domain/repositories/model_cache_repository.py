"""ModelCacheRepository - Port interface for ML model caching."""
from abc import ABC, abstractmethod
from typing import Any, Optional


class ModelCacheRepository(ABC):
    """Port interface for ML model caching.
    
    This abstraction allows the domain to remain pure Python while
    the infrastructure layer provides the actual caching implementation
    (e.g., using torch, diffusers, or a custom cache).
    """

    @abstractmethod
    def get_pipeline(self) -> Optional[Any]:
        """Get the loaded ML pipeline.
        
        Returns:
            The cached pipeline instance, or None if not loaded.
        """
        pass

    @abstractmethod
    def is_loaded(self) -> bool:
        """Check if the pipeline is currently loaded in cache.
        
        Returns:
            True if pipeline is loaded, False otherwise.
        """
        pass

    @abstractmethod
    def clear(self) -> None:
        """Clear the cached pipeline and free resources."""
        pass

    @abstractmethod
    def load(self, model_id: str) -> Any:
        """Load a pipeline into cache.
        
        Args:
            model_id: The identifier of the model to load.
            
        Returns:
            The loaded pipeline instance.
        """
        pass
