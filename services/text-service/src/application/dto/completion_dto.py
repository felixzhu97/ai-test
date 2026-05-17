"""Completion DTOs for Application Layer."""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any


@dataclass
class CompletionRequestDTO:
    """DTO for text completion request."""
    prompt: str
    system_prompt: Optional[str] = None
    provider: Optional[str] = None
    model: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 4096


@dataclass
class CompletionResponseDTO:
    """DTO for text completion response."""
    text: str
    provider: str
    model: str
    usage: Dict[str, Any] = field(default_factory=dict)
    finish_reason: Optional[str] = None
