"""AgentRed SDK Exceptions."""


class AgentRedError(Exception):
    """Base exception for all AgentRed SDK errors."""
    pass


class AuthError(AgentRedError):
    """Authentication failed (invalid API key, missing credentials)."""
    pass


class RateLimitError(AgentRedError):
    """Rate limit exceeded."""
    pass


class ScanError(AgentRedError):
    """Scan-related error (timeout, failure, invalid state)."""
    pass


class NotFoundError(AgentRedError):
    """Resource not found."""
    pass


class ValidationError(AgentRedError):
    """Request validation error."""
    pass
