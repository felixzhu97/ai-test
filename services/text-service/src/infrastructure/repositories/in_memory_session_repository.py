"""In-memory session repository implementation."""

from typing import Optional

from src.domain import Session, SessionRepository


class InMemorySessionRepository(SessionRepository):
    """In-memory implementation of SessionRepository.
    
    This is a simple implementation suitable for development and testing.
    For production, use RedisSessionRepository or similar.
    """
    
    def __init__(self):
        self._sessions: dict[str, Session] = {}
    
    def get(self, session_id: str) -> Optional[Session]:
        """Get session by ID."""
        return self._sessions.get(session_id)
    
    def save(self, session: Session) -> None:
        """Save or update a session."""
        self._sessions[session.id] = session
    
    def delete(self, session_id: str) -> bool:
        """Delete session by ID."""
        if session_id in self._sessions:
            del self._sessions[session_id]
            return True
        return False
    
    def exists(self, session_id: str) -> bool:
        """Check if session exists."""
        return session_id in self._sessions
    
    def clear(self) -> None:
        """Clear all sessions (for testing)."""
        self._sessions.clear()
    
    def __len__(self) -> int:
        """Get number of sessions."""
        return len(self._sessions)
