from dataclasses import dataclass
from typing import Optional


@dataclass
class ChatMessage:
    """Chat message value object."""
    role: str
    content: str
    name: Optional[str] = None

    def to_dict(self) -> dict:
        result = {"role": self.role, "content": self.content}
        if self.name:
            result["name"] = self.name
        return result

    @classmethod
    def from_dict(cls, data: dict) -> "ChatMessage":
        return cls(
            role=data.get("role", "user"),
            content=data.get("content", ""),
            name=data.get("name"),
        )
