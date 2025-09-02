"""Tests for shadowlink.exceptions module.

This module contains comprehensive tests for all custom exception classes
in the ShadowLink package, ensuring 100% test coverage.
"""

import pytest
from shadowlink.exceptions import (
    ShadowLinkError,
    ValidationError,
    URLShorteningError,
    MaskingError,
    NetworkError,
    ConfigurationError,
)


class TestShadowLinkError:
    """Test cases for the base ShadowLinkError exception."""

    def test_basic_instantiation(self):
        """Test basic exception instantiation."""
        error = ShadowLinkError("Test error message")
        assert str(error) == "Test error message"
        assert isinstance(error, Exception)

    def test_empty_message(self):
        """Test exception with empty message."""
        error = ShadowLinkError("")
        assert str(error) == ""

    def test_inheritance(self):
        """Test that ShadowLinkError inherits from Exception."""
        error = ShadowLinkError("Test")
        assert isinstance(error, Exception)
        assert isinstance(error, ShadowLinkError)


class TestValidationError:
    """Test cases for ValidationError exception."""

    def test_basic_instantiation(self):
        """Test basic ValidationError instantiation."""
        error = ValidationError("Invalid input")
        assert str(error) == "Invalid input"
        assert error.message == "Invalid input"
        assert error.field is None
        assert error.value is None
        assert isinstance(error, ShadowLinkError)

    def test_with_field_and_value(self):
        """Test ValidationError with field and value."""
        error = ValidationError("Invalid URL", field="url", value="invalid-url")
        assert str(error) == "Invalid URL"
        assert error.message == "Invalid URL"
        assert error.field == "url"
        assert error.value == "invalid-url"

    def test_with_field_only(self):
        """Test ValidationError with field only."""
        error = ValidationError("Field required", field="email")
        assert error.message == "Field required"
        assert error.field == "email"
        assert error.value is None

    def test_with_value_only(self):
        """Test ValidationError with value only."""
        error = ValidationError("Invalid format", value="test@")
        assert error.message == "Invalid format"
        assert error.field is None
        assert error.value == "test@"

    def test_inheritance(self):
        """Test ValidationError inheritance."""
        error = ValidationError("Test")
        assert isinstance(error, ShadowLinkError)
        assert isinstance(error, Exception)


class TestURLShorteningError:
    """Test cases for URLShorteningError exception."""

    def test_basic_instantiation(self):
        """Test basic URLShorteningError instantiation."""
        error = URLShorteningError("Service unavailable")
        assert str(error) == "Service unavailable"
        assert error.message == "Service unavailable"
        assert error.service is None
        assert error.original_error is None
        assert isinstance(error, ShadowLinkError)

    def test_with_service(self):
        """Test URLShorteningError with service."""
        error = URLShorteningError("API error", service="bit.ly")
        assert error.message == "API error"
        assert error.service == "bit.ly"
        assert error.original_error is None

    def test_with_original_error(self):
        """Test URLShorteningError with original error."""
        original = ValueError("Connection failed")
        error = URLShorteningError("Network issue", original_error=original)
        assert error.message == "Network issue"
        assert error.service is None
        assert error.original_error is original

    def test_with_all_parameters(self):
        """Test URLShorteningError with all parameters."""
        original = ConnectionError("Timeout")
        error = URLShorteningError("Complete failure", service="tinyurl", original_error=original)
        assert error.message == "Complete failure"
        assert error.service == "tinyurl"
        assert error.original_error is original

    def test_inheritance(self):
        """Test URLShorteningError inheritance."""
        error = URLShorteningError("Test")
        assert isinstance(error, ShadowLinkError)
        assert isinstance(error, Exception)


class TestMaskingError:
    """Test cases for MaskingError exception."""

    def test_basic_instantiation(self):
        """Test basic MaskingError instantiation."""
        error = MaskingError("Masking failed")
        assert str(error) == "Masking failed"
        assert error.message == "Masking failed"
        assert error.domain is None
        assert error.keyword is None
        assert error.url is None
        assert isinstance(error, ShadowLinkError)

    def test_with_domain(self):
        """Test MaskingError with domain."""
        error = MaskingError("Invalid domain", domain="example.com")
        assert error.message == "Invalid domain"
        assert error.domain == "example.com"
        assert error.keyword is None
        assert error.url is None

    def test_with_keyword(self):
        """Test MaskingError with keyword."""
        error = MaskingError("Invalid keyword", keyword="test-keyword")
        assert error.message == "Invalid keyword"
        assert error.domain is None
        assert error.keyword == "test-keyword"
        assert error.url is None

    def test_with_url(self):
        """Test MaskingError with URL."""
        error = MaskingError("Invalid URL", url="https://example.com")
        assert error.message == "Invalid URL"
        assert error.domain is None
        assert error.keyword is None
        assert error.url == "https://example.com"

    def test_with_all_parameters(self):
        """Test MaskingError with all parameters."""
        error = MaskingError(
            "Complete masking failure",
            domain="mask.com",
            keyword="secret",
            url="https://target.com",
        )
        assert error.message == "Complete masking failure"
        assert error.domain == "mask.com"
        assert error.keyword == "secret"
        assert error.url == "https://target.com"

    def test_inheritance(self):
        """Test MaskingError inheritance."""
        error = MaskingError("Test")
        assert isinstance(error, ShadowLinkError)
        assert isinstance(error, Exception)


class TestNetworkError:
    """Test cases for NetworkError exception."""

    def test_basic_instantiation(self):
        """Test basic NetworkError instantiation."""
        error = NetworkError("Connection failed")
        assert str(error) == "Connection failed"
        assert error.message == "Connection failed"
        assert error.service is None
        assert error.status_code is None
        assert isinstance(error, ShadowLinkError)

    def test_with_service(self):
        """Test NetworkError with service."""
        error = NetworkError("Service unreachable", service="api.example.com")
        assert error.message == "Service unreachable"
        assert error.service == "api.example.com"
        assert error.status_code is None

    def test_with_status_code(self):
        """Test NetworkError with status code."""
        error = NetworkError("HTTP error", status_code=404)
        assert error.message == "HTTP error"
        assert error.service is None
        assert error.status_code == 404

    def test_with_all_parameters(self):
        """Test NetworkError with all parameters."""
        error = NetworkError("Server error", service="api.test.com", status_code=500)
        assert error.message == "Server error"
        assert error.service == "api.test.com"
        assert error.status_code == 500

    def test_with_zero_status_code(self):
        """Test NetworkError with zero status code."""
        error = NetworkError("Connection refused", status_code=0)
        assert error.status_code == 0

    def test_inheritance(self):
        """Test NetworkError inheritance."""
        error = NetworkError("Test")
        assert isinstance(error, ShadowLinkError)
        assert isinstance(error, Exception)


class TestConfigurationError:
    """Test cases for ConfigurationError exception."""

    def test_basic_instantiation(self):
        """Test basic ConfigurationError instantiation."""
        error = ConfigurationError("Config missing")
        assert str(error) == "Config missing"
        assert error.message == "Config missing"
        assert error.config_key is None
        assert isinstance(error, ShadowLinkError)

    def test_with_config_key(self):
        """Test ConfigurationError with config key."""
        error = ConfigurationError("Missing API key", config_key="api_key")
        assert error.message == "Missing API key"
        assert error.config_key == "api_key"

    def test_with_empty_config_key(self):
        """Test ConfigurationError with empty config key."""
        error = ConfigurationError("Invalid config", config_key="")
        assert error.message == "Invalid config"
        assert error.config_key == ""

    def test_inheritance(self):
        """Test ConfigurationError inheritance."""
        error = ConfigurationError("Test")
        assert isinstance(error, ShadowLinkError)
        assert isinstance(error, Exception)


class TestExceptionHierarchy:
    """Test cases for exception hierarchy and relationships."""

    def test_all_exceptions_inherit_from_shadowlink_error(self):
        """Test that all custom exceptions inherit from ShadowLinkError."""
        exceptions = [
            ValidationError("test"),
            URLShorteningError("test"),
            MaskingError("test"),
            NetworkError("test"),
            ConfigurationError("test"),
        ]

        for exception in exceptions:
            assert isinstance(exception, ShadowLinkError)
            assert isinstance(exception, Exception)

    def test_exception_catching_by_base_class(self):
        """Test that all exceptions can be caught by ShadowLinkError."""
        exceptions = [
            ValidationError("validation failed"),
            URLShorteningError("shortening failed"),
            MaskingError("masking failed"),
            NetworkError("network failed"),
            ConfigurationError("config failed"),
        ]

        for exception in exceptions:
            try:
                raise exception
            except ShadowLinkError as e:
                assert str(e) in [
                    "validation failed",
                    "shortening failed",
                    "masking failed",
                    "network failed",
                    "config failed",
                ]
            except Exception:
                pytest.fail("Exception should have been caught as ShadowLinkError")

    def test_specific_exception_catching(self):
        """Test that specific exceptions can be caught individually."""
        # Test ValidationError
        try:
            raise ValidationError("test validation", field="email")
        except ValidationError as e:
            assert e.field == "email"

        # Test URLShorteningError
        try:
            raise URLShorteningError("test shortening", service="bit.ly")
        except URLShorteningError as e:
            assert e.service == "bit.ly"

        # Test MaskingError
        try:
            raise MaskingError("test masking", domain="test.com")
        except MaskingError as e:
            assert e.domain == "test.com"

        # Test NetworkError
        try:
            raise NetworkError("test network", status_code=404)
        except NetworkError as e:
            assert e.status_code == 404

        # Test ConfigurationError
        try:
            raise ConfigurationError("test config", config_key="api_key")
        except ConfigurationError as e:
            assert e.config_key == "api_key"
