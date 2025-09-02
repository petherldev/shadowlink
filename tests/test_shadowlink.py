"""Comprehensive unit tests for shadowlink.shadowlink module."""

import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
from io import StringIO

from shadowlink.shadowlink import (
    validate_url,
    validate_domain,
    validate_keyword,
    mask_url,
    get_user_input,
    generate_masked_urls,
    loading_spinner,
    show_banner,
    main,
)
from shadowlink.exceptions import (
    ValidationError,
    URLShorteningError,
    MaskingError,
    NetworkError,
)


class TestValidateUrl:
    """Test cases for URL validation functionality."""

    def test_validate_url_valid_cases(self):
        """Test validation of valid URLs."""
        valid_urls = [
            "https://example.com",
            "http://site.org/path?query=123",
            "https://sub.domain.co.uk:8080/path",
            "http://localhost:3000",
            "https://api.service.com/v1/endpoint",
        ]

        for url in valid_urls:
            result = validate_url(url)
            assert result is not None, f"URL should be valid: {url}"

    def test_validate_url_invalid_cases(self):
        """Test validation of invalid URLs."""
        invalid_urls = [
            "not_a_url",
            "ftp://invalid.com",
            "http:/missing-slash.com",
            "https://",
            "://example.com",
            "",
            "   ",
        ]

        for url in invalid_urls:
            with pytest.raises(ValidationError) as exc_info:
                validate_url(url)
            assert exc_info.value.field == "url"

    def test_validate_url_none_and_non_string(self):
        """Test validation with None and non-string inputs."""
        with pytest.raises(ValidationError) as exc_info:
            validate_url(None)
        assert "must be a non-empty string" in exc_info.value.message

        with pytest.raises(ValidationError) as exc_info:
            validate_url(123)
        assert "must be a non-empty string" in exc_info.value.message


class TestValidateDomain:
    """Test cases for domain validation functionality."""

    def test_validate_domain_valid_cases(self):
        """Test validation of valid domains."""
        valid_domains = [
            "google.com",
            "sub.domain.co.uk",
            "example.org",
            "test-site.net",
            "a.b.c.d.com",
        ]

        for domain in valid_domains:
            result = validate_domain(domain)
            assert result is not None, f"Domain should be valid: {domain}"

    def test_validate_domain_invalid_cases(self):
        """Test validation of invalid domains."""
        invalid_domains = [
            "no-tld",
            "in valid.com",
            "domain.",
            ".domain.com",
            "domain..com",
            "",
            "   ",
        ]

        for domain in invalid_domains:
            with pytest.raises(ValidationError) as exc_info:
                validate_domain(domain)
            assert exc_info.value.field == "domain"

    def test_validate_domain_edge_cases(self):
        """Test domain validation edge cases."""
        with pytest.raises(ValidationError) as exc_info:
            validate_domain(".example.com")
        assert "cannot start or end with a dot" in exc_info.value.message

        with pytest.raises(ValidationError) as exc_info:
            validate_domain("example..com")
        assert "consecutive dots" in exc_info.value.message


class TestValidateKeyword:
    """Test cases for keyword validation functionality."""

    def test_validate_keyword_valid_cases(self):
        """Test validation of valid keywords."""
        valid_keywords = [
            "login",
            "verify123",
            "test-keyword",
            "a",
            "123456789012345",  # exactly 15 chars
        ]

        for keyword in valid_keywords:
            result = validate_keyword(keyword)
            assert result is True, f"Keyword should be valid: {keyword}"

    def test_validate_keyword_invalid_cases(self):
        """Test validation of invalid keywords."""
        invalid_cases = [
            ("this has spaces", "contain letters, numbers, and hyphens"),
            ("toolongkeywordfortest", "15 characters or less"),
            ("-startswithhyphen", "cannot start or end with a hyphen"),
            ("endswithhyphen-", "cannot start or end with a hyphen"),
            ("special@chars", "contain letters, numbers, and hyphens"),
            ("", "cannot be empty"),
            ("   ", "cannot be empty"),
        ]

        for keyword, expected_error in invalid_cases:
            with pytest.raises(ValidationError) as exc_info:
                validate_keyword(keyword)
            assert expected_error in exc_info.value.message
            assert exc_info.value.field == "keyword"

    def test_validate_keyword_none_and_non_string(self):
        """Test keyword validation with None and non-string inputs."""
        with pytest.raises(ValidationError) as exc_info:
            validate_keyword(None)
        assert "must be a non-empty string" in exc_info.value.message


class TestMaskUrl:
    """Test cases for URL masking functionality."""

    def test_mask_url_success(self):
        """Test successful URL masking."""
        short_url = "https://tinyurl.com/abc123"
        masked = mask_url("facebook.com", "login", short_url)
        expected = "https://facebook.com-login@tinyurl.com/abc123"
        assert masked == expected

    def test_mask_url_with_path(self):
        """Test URL masking with path components."""
        short_url = "https://bit.ly/xyz789/path"
        masked = mask_url("google.com", "verify", short_url)
        expected = "https://google.com-verify@bit.ly/xyz789/path"
        assert masked == expected

    def test_mask_url_missing_parameters(self):
        """Test URL masking with missing parameters."""
        with pytest.raises(MaskingError) as exc_info:
            mask_url("", "keyword", "https://example.com")
        assert "All parameters" in exc_info.value.message

        with pytest.raises(MaskingError) as exc_info:
            mask_url("domain.com", "", "https://example.com")
        assert "All parameters" in exc_info.value.message

    def test_mask_url_invalid_short_url(self):
        """Test URL masking with invalid short URL."""
        with pytest.raises(MaskingError) as exc_info:
            mask_url("domain.com", "keyword", "invalid-url")
        assert "Invalid short URL format" in exc_info.value.message


class TestGetUserInput:
    """Test cases for user input functionality."""

    @patch("builtins.input")
    def test_get_user_input_valid_first_try(self, mock_input):
        """Test getting valid user input on first attempt."""
        mock_input.return_value = "valid-input"
        validator = lambda x: x == "valid-input"

        result = get_user_input("Enter input: ", validator, "Invalid input")
        assert result == "valid-input"
        mock_input.assert_called_once_with("Enter input: ")

    @patch("builtins.input")
    @patch("builtins.print")
    def test_get_user_input_retry_logic(self, mock_print, mock_input):
        """Test user input retry logic with validation errors."""
        # First two attempts fail validation, third succeeds
        mock_input.side_effect = ["invalid1", "invalid2", "valid"]

        def validator(x):
            if x == "valid":
                return True
            raise ValidationError(f"Invalid: {x}")

        result = get_user_input("Enter input: ", validator, "Try again")
        assert result == "valid"
        assert mock_input.call_count == 3

    @patch("builtins.input")
    def test_get_user_input_keyboard_interrupt(self, mock_input):
        """Test handling of keyboard interrupt during input."""
        mock_input.side_effect = KeyboardInterrupt()

        with pytest.raises(KeyboardInterrupt):
            get_user_input("Enter input: ", lambda x: True, "Error")

    @patch("builtins.input")
    def test_get_user_input_max_retries_exceeded(self, mock_input):
        """Test behavior when maximum retries are exceeded."""
        mock_input.return_value = "always-invalid"

        def validator(x):
            raise ValidationError("Always invalid")

        with pytest.raises(ValidationError) as exc_info:
            get_user_input("Enter input: ", validator, "Error")
        assert "Maximum retry attempts" in exc_info.value.message


class TestGenerateMaskedUrls:
    """Test cases for masked URL generation functionality."""

    @patch("shadowlink.shadowlink.pyshorteners.Shortener")
    def test_generate_masked_urls_success(self, mock_shortener_class):
        """Test successful generation of masked URLs."""
        # Mock the shortener services
        mock_shortener = Mock()
        mock_shortener_class.return_value = mock_shortener

        # Mock service methods
        mock_tinyurl = Mock()
        mock_tinyurl.short.return_value = "https://tinyurl.com/abc123"
        mock_dagd = Mock()
        mock_dagd.short.return_value = "https://da.gd/xyz789"

        mock_shortener.tinyurl = mock_tinyurl
        mock_shortener.dagd = mock_dagd
        mock_shortener.clckru = Mock(side_effect=Exception("Service unavailable"))
        mock_shortener.osdb = Mock(side_effect=Exception("Service unavailable"))

        result = generate_masked_urls("https://example.com", "facebook.com", "login")

        assert len(result) == 2
        assert "facebook.com-login@tinyurl.com" in result[0]
        assert "facebook.com-login@da.gd" in result[1]

    @patch("shadowlink.shadowlink.pyshorteners.Shortener")
    def test_generate_masked_urls_all_services_fail(self, mock_shortener_class):
        """Test behavior when all shortening services fail."""
        mock_shortener = Mock()
        mock_shortener_class.return_value = mock_shortener

        # Make all services fail
        for service_name in ["tinyurl", "dagd", "clckru", "osdb"]:
            service_mock = Mock()
            service_mock.short.side_effect = Exception("Service unavailable")
            setattr(mock_shortener, service_name, service_mock)

        with pytest.raises(NetworkError) as exc_info:
            generate_masked_urls("https://example.com", "facebook.com", "login")
        assert "All URL shortening services failed" in exc_info.value.message


class TestUtilityFunctions:
    """Test cases for utility functions."""

    @patch("sys.stdout")
    @patch("time.sleep")
    def test_loading_spinner(self, mock_sleep, mock_stdout):
        """Test loading spinner functionality."""
        loading_spinner("test message")

        # Verify sleep was called the expected number of times
        expected_calls = 12 * 4  # SPINNER_ITERATIONS * frames
        assert mock_sleep.call_count == expected_calls

        # Verify stdout.write was called
        assert mock_stdout.write.called
        assert mock_stdout.flush.called

    @patch("builtins.print")
    def test_show_banner(self, mock_print):
        """Test banner display functionality."""
        show_banner()

        # Verify print was called multiple times for banner and metadata
        assert mock_print.call_count >= 4

        # Check that version, author, and GitHub info are printed
        printed_text = " ".join([str(call.args[0]) for call in mock_print.call_args_list])
        assert "Version" in printed_text
        assert "Author" in printed_text
        assert "GitHub" in printed_text


class TestMainFunction:
    """Test cases for the main CLI function."""

    @patch("shadowlink.shadowlink.show_banner")
    @patch("shadowlink.shadowlink.get_user_input")
    @patch("shadowlink.shadowlink.loading_spinner")
    @patch("shadowlink.shadowlink.generate_masked_urls")
    @patch("builtins.print")
    def test_main_success_flow(
        self, mock_print, mock_generate, mock_spinner, mock_input, mock_banner
    ):
        """Test successful execution of main function."""
        # Mock user inputs
        mock_input.side_effect = ["https://example.com", "facebook.com", "login"]

        # Mock URL generation
        mock_generate.return_value = [
            "https://facebook.com-login@tinyurl.com/abc123",
            "https://facebook.com-login@da.gd/xyz789",
        ]

        main()

        # Verify all components were called
        mock_banner.assert_called_once()
        assert mock_input.call_count == 3
        mock_spinner.assert_called_once()
        mock_generate.assert_called_once_with("https://example.com", "facebook.com", "login")

        # Verify success message was printed
        printed_calls = [str(call.args[0]) for call in mock_print.call_args_list]
        success_messages = [msg for msg in printed_calls if "Successfully generated" in msg]
        assert len(success_messages) > 0

    @patch("shadowlink.shadowlink.show_banner")
    @patch("shadowlink.shadowlink.get_user_input")
    @patch("sys.exit")
    def test_main_keyboard_interrupt(self, mock_exit, mock_input, mock_banner):
        """Test main function handling of keyboard interrupt."""
        mock_input.side_effect = KeyboardInterrupt()

        main()

        mock_exit.assert_called_once_with(1)

    @patch("shadowlink.shadowlink.show_banner")
    @patch("shadowlink.shadowlink.get_user_input")
    @patch("sys.exit")
    def test_main_validation_error(self, mock_exit, mock_input, mock_banner):
        """Test main function handling of validation errors."""
        mock_input.side_effect = ValidationError("Invalid input", field="test")

        main()

        mock_exit.assert_called_once_with(1)

    @patch("shadowlink.shadowlink.show_banner")
    @patch("shadowlink.shadowlink.get_user_input")
    @patch("shadowlink.shadowlink.generate_masked_urls")
    @patch("sys.exit")
    def test_main_network_error(self, mock_exit, mock_generate, mock_input, mock_banner):
        """Test main function handling of network errors."""
        mock_input.side_effect = ["https://example.com", "facebook.com", "login"]
        mock_generate.side_effect = NetworkError("All services failed")

        main()

        mock_exit.assert_called_once_with(1)


class TestExceptionIntegration:
    """Test cases for exception handling integration."""

    def test_validation_error_attributes(self):
        """Test ValidationError exception attributes."""
        error = ValidationError("Test message", field="test_field", value="test_value")

        assert str(error) == "Test message"
        assert error.field == "test_field"
        assert error.value == "test_value"
        assert error.message == "Test message"

    def test_masking_error_attributes(self):
        """Test MaskingError exception attributes."""
        error = MaskingError(
            "Test message", domain="test.com", keyword="test", url="http://test.com"
        )

        assert str(error) == "Test message"
        assert error.domain == "test.com"
        assert error.keyword == "test"
        assert error.url == "http://test.com"

    def test_network_error_attributes(self):
        """Test NetworkError exception attributes."""
        error = NetworkError("Test message", service="TestService", status_code=404)

        assert str(error) == "Test message"
        assert error.service == "TestService"
        assert error.status_code == 404


@pytest.fixture
def sample_urls():
    """Fixture providing sample URLs for testing."""
    return {
        "valid": ["https://example.com", "http://test.org/path", "https://sub.domain.co.uk:8080"],
        "invalid": ["not-a-url", "ftp://invalid.com", "http:/missing-slash"],
    }


@pytest.fixture
def sample_domains():
    """Fixture providing sample domains for testing."""
    return {
        "valid": ["google.com", "sub.example.org", "test-site.net"],
        "invalid": ["no-tld", ".starts-with-dot.com", "ends-with-dot.com."],
    }


@pytest.fixture
def sample_keywords():
    """Fixture providing sample keywords for testing."""
    return {
        "valid": ["login", "verify123", "test-keyword"],
        "invalid": ["has spaces", "toolongkeywordfortest", "-starts-with-hyphen"],
    }


class TestIntegration:
    """Integration tests for complete workflows."""

    @patch("shadowlink.shadowlink.pyshorteners.Shortener")
    def test_complete_url_masking_workflow(self, mock_shortener_class):
        """Test complete workflow from validation to masking."""
        # Setup mocks
        mock_shortener = Mock()
        mock_shortener_class.return_value = mock_shortener
        mock_tinyurl = Mock()
        mock_tinyurl.short.return_value = "https://tinyurl.com/test123"
        mock_shortener.tinyurl = mock_tinyurl
        mock_shortener.dagd = Mock(side_effect=Exception("Service down"))
        mock_shortener.clckru = Mock(side_effect=Exception("Service down"))
        mock_shortener.osdb = Mock(side_effect=Exception("Service down"))

        # Test the complete workflow
        url = "https://example.com/long/path?param=value"
        domain = "facebook.com"
        keyword = "login"

        # Validate inputs
        assert validate_url(url) is not None
        assert validate_domain(domain) is not None
        assert validate_keyword(keyword) is True

        # Generate masked URLs
        result = generate_masked_urls(url, domain, keyword)

        assert len(result) == 1
        assert "facebook.com-login@tinyurl.com" in result[0]
