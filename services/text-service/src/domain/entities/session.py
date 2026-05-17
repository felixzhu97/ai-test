from dataclasses import dataclass, field
from typing import List, Optional
import uuid

from .message import ChatMessage


@dataclass
class Session:
    """Chat session aggregate root."""
    id: str
    messages: List[ChatMessage] = field(default_factory=list)
    max_history: int = 20

    def add_user_message(self, content: str) -> None:
        """Add a user message to the session."""
        self.messages.append(ChatMessage(role="user", content=content))
        self._trim_history()

    def add_assistant_message(self, content: str) -> None:
        """Add an assistant message to the session."""
        self.messages.append(ChatMessage(role="assistant", content=content))
        self._trim_history()

    def _trim_history(self) -> None:
        """Trim history to max_history messages."""
        if len(self.messages) > self.max_history:
            self.messages = self.messages[-self.max_history:]

    def get_conversation(self, system_prompt: Optional[str] = None) -> List[dict]:
        """Get conversation as list of dicts for LLM."""
        result = []
        if system_prompt:
            result.append({"role": "system", "content": system_prompt})
        result.extend([msg.to_dict() for msg in self.messages])
        return result

    @classmethod
    def create(cls, session_id: Optional[str] = None) -> "Session":
        """Factory method to create a new session."""
        return cls(id=session_id or str(uuid.uuid4()))
