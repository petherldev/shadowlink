"""Comprehensive tests for output module functions."""

import csv
import json
import sys
from io import StringIO
from pathlib import Path
from unittest.mock import Mock, patch, mock_open
import pytest

from shadowlink.output import OutputFormatter
from shadowlink.config import ShadowLinkConfig


class TestOutputFormatter:
    """Test OutputFormatter class methods."""

    def test_init_with_colors_enabled(self):
        """Test OutputFormatter initialization with colors enabled."""
        config = ShadowLinkConfig(colored_output=True)

        with patch("sys.stdout.isatty", return_value=True):
            formatter = OutputFormatter(config)

            assert formatter.config == config
            assert formatter.colors_enabled is True

    def test_init_with_colors_disabled(self):
        """Test OutputFormatter initialization with colors disabled."""
        config = ShadowLinkConfig(colored_output=False)

        formatter = OutputFormatter(config)

        assert formatter.colors_enabled is False

    def test_init_no_tty(self):
        """Test OutputFormatter initialization when not in TTY."""
        config = ShadowLinkConfig(colored_output=True)

        with patch("sys.stdout.isatty", return_value=False):
            formatter = OutputFormatter(config)

            assert formatter.colors_enabled is False

    def test_colorize_enabled(self):
        """Test _colorize method with colors enabled."""
        config = ShadowLinkConfig(colored_output=True)

        with patch("sys.stdout.isatty", return_value=True):
            formatter = OutputFormatter(config)

            result = formatter._colorize("test", "\033[31m")

            assert result == "\033[31mtest\033[0m"

    def test_colorize_disabled(self):
        """Test _colorize method with colors disabled."""
        config = ShadowLinkConfig(colored_output=False)
        formatter = OutputFormatter(config)

        result = formatter._colorize("test", "\033[31m")

        assert result == "test"

    def test_format_console_single_success(self):
        """Test console formatting for single successful result."""
        config = ShadowLinkConfig(colored_output=False)
        formatter = OutputFormatter(config)

        results = [
            {
                "original_url": "https://example.com",
                "domain": "facebook.com",
                "keyword": "test",
                "success": True,
                "masked_urls": ["http://masked1.com", "http://masked2.com"],
                "errors": [],
            }
        ]

        output = formatter.format_console(results)

        assert "Original URL: https://example.com" in output
        assert "Domain: facebook.com" in output
        assert "Keyword: test" in output
        assert "[✓] Successfully generated masked URLs:" in output
        assert "➤ Link 1: http://masked1.com" in output
        assert "➤ Link 2: http://masked2.com" in output

    def test_format_console_single_failure(self):
        """Test console formatting for single failed result."""
        config = ShadowLinkConfig(colored_output=False)
        formatter = OutputFormatter(config)

        results = [
            {
                "original_url": "https://example.com",
                "domain": "facebook.com",
                "keyword": "test",
                "success": False,
                "masked_urls": [],
                "errors": ["ValidationError: Invalid URL"],
            }
        ]

        output = formatter.format_console(results)

        assert "[✖] Failed to generate URLs:" in output
        assert "Error: ValidationError: Invalid URL" in output

    def test_format_console_multiple_results(self):
        """Test console formatting for multiple results."""
        config = ShadowLinkConfig(colored_output=False)
        formatter = OutputFormatter(config)

        results = [
            {
                "original_url": "https://example1.com",
                "domain": "facebook.com",
                "keyword": "test1",
                "success": True,
                "masked_urls": ["http://masked1.com"],
                "errors": [],
            },
            {
                "original_url": "https://example2.com",
                "domain": "twitter.com",
                "keyword": "test2",
                "success": False,
                "masked_urls": [],
                "errors": ["Error occurred"],
            },
        ]

        output = formatter.format_console(results)

        assert "=== Result 1 ===" in output
        assert "=== Result 2 ===" in output
        assert "https://example1.com" in output
        assert "https://example2.com" in output

    def test_format_json(self):
        """Test JSON formatting."""
        config = ShadowLinkConfig()
        formatter = OutputFormatter(config)

        results = [
            {
                "original_url": "https://example.com",
                "domain": "facebook.com",
                "keyword": "test",
                "success": True,
                "masked_urls": ["http://masked1.com"],
                "errors": [],
            }
        ]

        output = formatter.format_json(results)
        parsed = json.loads(output)

        assert parsed["shadowlink_version"] == "0.0.1"
        assert parsed["total_processed"] == 1
        assert parsed["successful"] == 1
        assert parsed["failed"] == 0
        assert len(parsed["results"]) == 1
        assert parsed["results"][0]["original_url"] == "https://example.com"

    def test_format_csv(self):
        """Test CSV formatting."""
        config = ShadowLinkConfig()
        formatter = OutputFormatter(config)

        results = [
            {
                "original_url": "https://example.com",
                "domain": "facebook.com",
                "keyword": "test",
                "success": True,
                "masked_urls": ["http://masked1.com", "http://masked2.com"],
                "errors": [],
            }
        ]

        output = formatter.format_csv(results)
        lines = output.strip().split("\n")

        # Check header
        assert "original_url,domain,keyword,success" in lines[0]

        # Check data
        assert "https://example.com,facebook.com,test,True" in lines[1]
        assert "http://masked1.com" in lines[1]
        assert "http://masked2.com" in lines[1]

    def test_format_csv_with_errors(self):
        """Test CSV formatting with errors."""
        config = ShadowLinkConfig()
        formatter = OutputFormatter(config)

        results = [
            {
                "original_url": "https://example.com",
                "domain": "facebook.com",
                "keyword": "test",
                "success": False,
                "masked_urls": [],
                "errors": ["Error 1", "Error 2"],
            }
        ]

        output = formatter.format_csv(results)

        assert "Error 1; Error 2" in output

    @patch("shadowlink.output.YAML_AVAILABLE", True)
    @patch("shadowlink.output.yaml")
    def test_format_yaml_success(self, mock_yaml):
        """Test YAML formatting with yaml module available."""
        config = ShadowLinkConfig()
        formatter = OutputFormatter(config)
        mock_yaml.dump.return_value = "yaml_output"

        results = [{"test": "data", "success": True}]

        output = formatter.format_yaml(results)

        assert output == "yaml_output"
        mock_yaml.dump.assert_called_once()

    @patch("shadowlink.output.YAML_AVAILABLE", False)
    def test_format_yaml_fallback(self):
        """Test YAML formatting fallback to JSON when yaml not available."""
        config = ShadowLinkConfig()
        formatter = OutputFormatter(config)

        results = [{"test": "data", "success": True}]

        output = formatter.format_yaml(results)

        # Should fallback to JSON
        parsed = json.loads(output)
        assert "results" in parsed

    def test_output_results_console(self):
        """Test output_results with console format."""
        config = ShadowLinkConfig(output_format="console")
        formatter = OutputFormatter(config)

        results = [
            {
                "original_url": "https://example.com",
                "domain": "facebook.com",
                "keyword": "test",
                "success": True,
                "masked_urls": ["http://masked1.com"],
                "errors": [],
            }
        ]

        with patch("builtins.print") as mock_print:
            formatter.output_results(results)

            mock_print.assert_called_once()
            printed_output = mock_print.call_args[0][0]
            assert "Original URL: https://example.com" in printed_output

    def test_output_results_to_file(self):
        """Test output_results saving to file."""
        config = ShadowLinkConfig(
            output_format="json", should_save_to_file=True, output_file="output.json"
        )
        formatter = OutputFormatter(config)

        results = [{"test": "data", "success": True}]

        with (
            patch("builtins.open", mock_open()) as mock_file,
            patch("pathlib.Path.mkdir") as mock_mkdir,
            patch("builtins.print") as mock_print,
        ):

            formatter.output_results(results)

            mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)
            mock_file.assert_called_once_with(Path("output.json"), "w", encoding="utf-8")

            # Should also print summary
            mock_print.assert_called()

    def test_output_results_file_error(self):
        """Test output_results with file save error."""
        config = ShadowLinkConfig(
            output_format="json", should_save_to_file=True, output_file="output.json"
        )
        formatter = OutputFormatter(config)

        results = [{"test": "data", "success": True}]

        with (
            patch("builtins.open", side_effect=PermissionError("Access denied")),
            patch("builtins.print") as mock_print,
        ):

            formatter.output_results(results)

            # Should print error and fallback to console output
            mock_print.assert_any_call("✖ Failed to save output: Access denied")

    def test_output_results_invalid_format(self):
        """Test output_results with invalid format falls back to console."""
        config = ShadowLinkConfig(output_format="invalid_format")
        formatter = OutputFormatter(config)

        results = [
            {
                "original_url": "https://example.com",
                "domain": "facebook.com",
                "keyword": "test",
                "success": True,
                "masked_urls": ["http://masked1.com"],
                "errors": [],
            }
        ]

        with patch("builtins.print") as mock_print:
            formatter.output_results(results)

            # Should fallback to console format
            printed_output = mock_print.call_args[0][0]
            assert "Original URL: https://example.com" in printed_output

    def test_create_summary(self):
        """Test _create_summary method."""
        config = ShadowLinkConfig(colored_output=False, output_file="test.json")
        formatter = OutputFormatter(config)

        results = [{"success": True}, {"success": True}, {"success": False}]

        summary = formatter._create_summary(results)

        assert "Total URLs processed: 3" in summary
        assert "Successful: 2" in summary
        assert "Failed: 1" in summary
        assert "Results saved to: test.json" in summary

    def test_create_summary_no_file(self):
        """Test _create_summary method without output file."""
        config = ShadowLinkConfig(colored_output=False)
        formatter = OutputFormatter(config)

        results = [{"success": True}]

        summary = formatter._create_summary(results)

        assert "Total URLs processed: 1" in summary
        assert "Results saved to:" not in summary
