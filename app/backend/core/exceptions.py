class AppError(Exception):
    """Base application error."""


class NotFoundError(AppError):
    """Raised when a resource cannot be found."""


class ConflictError(AppError):
    """Raised when a resource violates a uniqueness rule."""


class AuthorizationError(AppError):
    """Raised when the user is not allowed to perform an action."""


class ProcessingError(AppError):
    """Raised when a data pipeline step fails."""
