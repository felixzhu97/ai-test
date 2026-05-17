class DomainError(Exception):
    """Base domain exception."""
    pass


class SessionNotFoundError(DomainError):
    """Raised when session is not found."""
    pass


class LLMServiceError(DomainError):
    """Raised when LLM service fails."""
    pass


class InvalidProviderError(DomainError):
    """Raised when provider is invalid."""
    pass


class InvalidMessageError(DomainError):
    """Raised when message format is invalid."""
    pass
