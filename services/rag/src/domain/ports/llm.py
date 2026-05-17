"""LLM Gateway port - abstract interface for language model operations."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, AsyncIterator

if TYPE_CHECKING:
    pass


@dataclass(frozen=True)
class Message:
    """
    Immutable message for LLM conversation.
    
    Attributes:
        role: Message role (system, user, assistant).
        content: The message content.
    """
    
    role: str
    content: str


@dataclass(frozen=True)
class LLMResponse:
    """
    Immutable response from LLM.
    
    Attributes:
        content: Generated text content.
        usage: Token usage statistics.
        model: Model identifier used.
        finish_reason: Reason for completion.
    """
    
    content: str
    usage: dict[str, int] = field(default_factory=dict)
    model: str = ""
    finish_reason: str = ""


class LLMGatewayPort(ABC):
    """
    Abstract interface for language model operations.
    
    This port defines the contract for interacting with
    large language models. Implementations can use OpenAI,
    Anthropic, Ollama, or any LLM provider.
    """
    
    @property
    @abstractmethod
    def provider(self) -> str:
        """
        Get the LLM provider name.
        
        Returns:
            Provider identifier (openai, anthropic, ollama, etc.).
        """
        pass
    
    @property
    @abstractmethod
    def model(self) -> str:
        """
        Get the model name.
        
        Returns:
            Model identifier.
        """
        pass
    
    @abstractmethod
    async def generate(
        self,
        messages: list[Message],
        temperature: float = 0.7,
        max_tokens: int | None = None,
        stream: bool = False,
    ) -> LLMResponse:
        """
        Generate text completion.
        
        Args:
            messages: List of conversation messages.
            temperature: Sampling temperature (0.0-2.0).
            max_tokens: Maximum tokens to generate.
            stream: Whether to stream the response.
            
        Returns:
            LLM response with generated content.
        """
        pass
    
    @abstractmethod
    async def stream_generate(
        self,
        messages: list[Message],
        temperature: float = 0.7,
        max_tokens: int | None = None,
    ) -> AsyncIterator[str]:
        """
        Stream text completion.
        
        Args:
            messages: List of conversation messages.
            temperature: Sampling temperature (0.0-2.0).
            max_tokens: Maximum tokens to generate.
            
        Yields:
            Text chunks as they are generated.
        """
        pass
