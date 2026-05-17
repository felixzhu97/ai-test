from enum import Enum
from typing import List


class LLMProvider(Enum):
    """Supported LLM providers."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    OLLAMA = "ollama"

    @classmethod
    def all(cls) -> List["LLMProvider"]:
        return list(cls)

    @classmethod
    def from_string(cls, value: str) -> "LLMProvider":
        """Create from string, case-insensitive."""
        for provider in cls:
            if provider.value.lower() == value.lower():
                return provider
        raise ValueError(f"Unknown provider: {value}")
