"""Configuration Adapter - Bridges config to infrastructure."""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from ...core.config import Settings


class ConfigPort(ABC):
    """Abstract protocol for configuration."""
    
    @property
    @abstractmethod
    def llm_provider(self) -> str:
        pass
    
    @property
    @abstractmethod
    def llm_model(self) -> str:
        pass
    
    @property
    @abstractmethod
    def llm_max_tokens(self) -> int:
        pass
    
    @property
    @abstractmethod
    def openai_api_key(self) -> Optional[str]:
        pass
    
    @property
    @abstractmethod
    def openai_base_url(self) -> Optional[str]:
        pass
    
    @property
    @abstractmethod
    def openai_timeout(self) -> int:
        pass
    
    @property
    @abstractmethod
    def anthropic_api_key(self) -> Optional[str]:
        pass
    
    @property
    @abstractmethod
    def anthropic_default_model(self) -> str:
        pass
    
    @property
    @abstractmethod
    def anthropic_timeout(self) -> int:
        pass
    
    @property
    @abstractmethod
    def ollama_base_url(self) -> str:
        pass
    
    @property
    @abstractmethod
    def ollama_model(self) -> str:
        pass
    
    @property
    @abstractmethod
    def ollama_timeout(self) -> int:
        pass


class PydanticConfigAdapter(ConfigPort):
    """Adapter for Pydantic Settings."""
    
    def __init__(self, settings: "Settings"):
        self._settings = settings
    
    @property
    def llm_provider(self) -> str:
        return self._settings.LLM_PROVIDER
    
    @property
    def llm_model(self) -> str:
        return self._settings.LLM_MODEL
    
    @property
    def llm_max_tokens(self) -> int:
        return self._settings.LLM_MAX_TOKENS
    
    @property
    def openai_api_key(self) -> Optional[str]:
        return self._settings.OPENAI_API_KEY or None
    
    @property
    def openai_base_url(self) -> Optional[str]:
        return self._settings.OPENAI_BASE_URL or None
    
    @property
    def openai_timeout(self) -> int:
        return self._settings.OPENAI_TIMEOUT
    
    @property
    def anthropic_api_key(self) -> Optional[str]:
        return self._settings.ANTHROPIC_API_KEY or None
    
    @property
    def anthropic_default_model(self) -> str:
        models = self._settings.ANTHROPIC_MODELS.split(",")
        return models[0].strip() if models else "claude-sonnet-4-20250514"
    
    @property
    def anthropic_timeout(self) -> int:
        return self._settings.ANTHROPIC_TIMEOUT
    
    @property
    def ollama_base_url(self) -> str:
        return self._settings.OLLAMA_BASE_URL
    
    @property
    def ollama_model(self) -> str:
        return self._settings.OLLAMA_MODEL
    
    @property
    def ollama_timeout(self) -> int:
        return self._settings.OLLAMA_TIMEOUT
