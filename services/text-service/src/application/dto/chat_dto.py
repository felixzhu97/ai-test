"""Chat DTOs for Application Layer."""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Iterator

from src.domain.entities.message import ChatMessage


@dataclass
class ChatMessageDTO:
    """DTO for chat message."""
    role: str
    content: str
    name: Optional[str] = None

    def to_domain(self) -> ChatMessage:
        """Convert to domain ChatMessage."""
        return ChatMessage(role=self.role, content=self.content, name=self.name)

    @classmethod
    def from_domain(cls, msg: ChatMessage) -> "ChatMessageDTO":
        """Create from domain ChatMessage."""
        return cls(role=msg.role, content=msg.content, name=msg.name)


@dataclass
class ChatRequestDTO:
    """DTO for chat completion request."""
    messages: List[ChatMessageDTO] = field(default_factory=list)
    system_prompt: Optional[str] = None
    provider: Optional[str] = None
    model: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 4096
    session_id: Optional[str] = None


@dataclass
class ChatResponseDTO:
    """DTO for chat completion response."""
    text: str
    provider: str
    model: str
    session_id: str
    usage: Dict[str, Any] = field(default_factory=dict)
    finish_reason: Optional[str] = None
