"""LLM Gateway Protocol - Interface for LLM services."""

from abc import ABC, abstractmethod
from typing import Optional, Iterator, List


class LLMGatewayPort(ABC):
    """Abstract protocol for LLM gateways.
    
    This protocol defines the interface that any LLM adapter must implement.
    The Application layer depends on this abstraction, not the concrete implementation.
    """
    
    @property
    @abstractmethod
    def default_provider(self) -> str:
        """Get the default provider name."""
        pass
    
    @property
    @abstractmethod
    def default_model(self) -> str:
        """Get the default model name."""
        pass
    
    @abstractmethod
    def complete(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> str:
        """Generate text completion.
        
        Args:
            prompt: Input prompt
            system_prompt: Optional system prompt
            provider: Provider override
            model: Model override
            temperature: Sampling temperature
            max_tokens: Max tokens to generate
            
        Returns:
            Generated text
        """
        pass
    
    @abstractmethod
    def complete_stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> Iterator[str]:
        """Generate streaming text completion.
        
        Yields:
            Text chunks as they are generated
        """
        pass
    
    @abstractmethod
    def chat(
        self,
        messages: List[dict],
        system_prompt: Optional[str] = None,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> str:
        """Generate chat completion.
        
        Args:
            messages: List of message dicts with role and content
            system_prompt: Optional system prompt override
            
        Returns:
            Generated response text
        """
        pass
    
    @abstractmethod
    def chat_stream(
        self,
        messages: List[dict],
        system_prompt: Optional[str] = None,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> Iterator[str]:
        """Generate streaming chat completion.
        
        Yields:
            Text chunks as they are generated
        """
        pass
    
    @abstractmethod
    def reset(self) -> None:
        """Reset cached LLM instance."""
        pass
