from abc import ABC, abstractmethod
from typing import Optional

from ..entities.session import Session


class SessionRepository(ABC):
    """Abstract repository for session storage."""

    @abstractmethod
    def get(self, session_id: str) -> Optional[Session]:
        """Get session by ID, returns None if not found."""
        pass

    @abstractmethod
    def save(self, session: Session) -> None:
        """Save or update a session."""
        pass

    @abstractmethod
    def delete(self, session_id: str) -> bool:
        """Delete session by ID, returns True if deleted."""
        pass

    @abstractmethod
    def exists(self, session_id: str) -> bool:
        """Check if session exists."""
        pass
