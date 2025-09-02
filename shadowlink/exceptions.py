"""Custom exception classes for ShadowLink.

This module defines specific exception types for different error conditions
that can occur during URL cloaking operations, providing better error
handling and more informative error messages.
"""

from __future__ import annotations


class ShadowLinkError(Exception):
    """Base exception class for all ShadowLink-related errors.

    This serves as the parent class for all custom exceptions in the
    ShadowLink package, allowing for easy exception handling at different
    levels of granularity.
    """

    pass


class ValidationError(ShadowLinkError):
    """Raised when input validation fails.

    This exception is raised when user input (URLs, domains, keywords)
    fails validation checks, providing specific feedback about what
    went wrong with the input.
    """

    def __init__(self, message: str, field: str = None, value: str = None):
        """Initialize validation error with detailed context.

        Args:
            message: Human-readable error message
            field: The field that failed validation (optional)
            value: The invalid value that was provided (optional)
        """
        super().__init__(message)
        self.field = field
        self.value = value
        self.message = message


class URLShorteningError(ShadowLinkError):
    """Raised when URL shortening operations fail.

    This exception is raised when external URL shortening services
    are unavailable, return errors, or fail to process the request.
    """

    def __init__(self, message: str, service: str = None, original_error: Exception = None):
        """Initialize URL shortening error with service context.

        Args:
            message: Human-readable error message
            service: The shortening service that failed (optional)
            original_error: The underlying exception that caused the failure (optional)
        """
        super().__init__(message)
        self.service = service
        self.original_error = original_error
        self.message = message


class MaskingError(ShadowLinkError):
    """Raised when URL masking operations fail.

    This exception is raised when the process of creating masked URLs
    fails due to invalid input parameters or URL parsing issues.
    """

    def __init__(self, message: str, domain: str = None, keyword: str = None, url: str = None):
        """Initialize masking error with operation context.

        Args:
            message: Human-readable error message
            domain: The domain used for masking (optional)
            keyword: The keyword used for masking (optional)
            url: The URL being masked (optional)
        """
        super().__init__(message)
        self.domain = domain
        self.keyword = keyword
        self.url = url
        self.message = message


class NetworkError(ShadowLinkError):
    """Raised when network operations fail.

    This exception is raised when network connectivity issues prevent
    the application from communicating with external services.
    """

    def __init__(self, message: str, service: str = None, status_code: int = None):
        """Initialize network error with connection context.

        Args:
            message: Human-readable error message
            service: The service that couldn't be reached (optional)
            status_code: HTTP status code if applicable (optional)
        """
        super().__init__(message)
        self.service = service
        self.status_code = status_code
        self.message = message


class ConfigurationError(ShadowLinkError):
    """Raised when configuration or setup issues are detected.

    This exception is raised when the application encounters problems
    with its configuration, missing dependencies, or environment setup.
    """

    def __init__(self, message: str, config_key: str = None):
        """Initialize configuration error with context.

        Args:
            message: Human-readable error message
            config_key: The configuration key that caused the issue (optional)
        """
        super().__init__(message)
        self.config_key = config_key
        self.message = message
