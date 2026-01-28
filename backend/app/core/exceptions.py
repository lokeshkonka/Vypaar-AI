"""Custom exceptions for the application."""

from typing import Any, Optional


class AgriTechException(Exception):
    """Base exception for all application errors."""

    def __init__(
        self,
        message: str,
        status_code: int = 500,
        details: Optional[dict[str, Any]] = None,
    ):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class ValidationError(AgriTechException):
    """Raised when data validation fails."""

    def __init__(self, message: str, details: Optional[dict[str, Any]] = None):
        super().__init__(message, status_code=400, details=details)


class NotFoundError(AgriTechException):
    """Raised when a resource is not found."""

    def __init__(self, message: str, details: Optional[dict[str, Any]] = None):
        super().__init__(message, status_code=404, details=details)


class DatabaseError(AgriTechException):
    """Raised when a database operation fails."""

    def __init__(self, message: str, details: Optional[dict[str, Any]] = None):
        super().__init__(message, status_code=500, details=details)


class ScraperError(AgriTechException):
    """Raised when web scraping fails."""

    def __init__(self, message: str, details: Optional[dict[str, Any]] = None):
        super().__init__(message, status_code=500, details=details)


class MLModelError(AgriTechException):
    """Raised when ML model operations fail."""

    def __init__(self, message: str, details: Optional[dict[str, Any]] = None):
        super().__init__(message, status_code=500, details=details)


class PredictionError(AgriTechException):
    """Raised when prediction fails."""

    def __init__(self, message: str, details: Optional[dict[str, Any]] = None):
        super().__init__(message, status_code=500, details=details)


class AlertError(AgriTechException):
    """Raised when alert operations fail."""

    def __init__(self, message: str, details: Optional[dict[str, Any]] = None):
        super().__init__(message, status_code=500, details=details)


class InventoryError(AgriTechException):
    """Raised when inventory operations fail."""

    def __init__(self, message: str, details: Optional[dict[str, Any]] = None):
        super().__init__(message, status_code=500, details=details)


class RateLimitError(AgriTechException):
    """Raised when rate limit is exceeded."""

    def __init__(self, message: str = "Rate limit exceeded", details: Optional[dict[str, Any]] = None):
        super().__init__(message, status_code=429, details=details)


class ConfigurationError(AgriTechException):
    """Raised when configuration is invalid."""

    def __init__(self, message: str, details: Optional[dict[str, Any]] = None):
        super().__init__(message, status_code=500, details=details)
