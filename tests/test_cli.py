"""Comprehensive tests for CLI module functions."""

import argparse
import json
import logging
import sys
from pathlib import Path
from unittest.mock import Mock, patch, mock_open, MagicMock
import pytest

from shadowlink.cli import (
    setup_logging,
    create_parser,
    process_single_url,
    process_batch_file,
    interactive_mode,
    main_cli,
)
from shadowlink.config import ShadowLinkConfig
from shadowlink.exceptions import ValidationError, NetworkError, MaskingError


class TestSetupLogging:
    """Test setup_logging function."""

    @patch("shadowlink.cli.logging.basicConfig")
    def test_setup_logging_basic_config(self, mock_basic_config):
        """Test basic logging configuration."""
        config = ShadowLinkConfig(log_level="DEBUG", log_format="test format")

        setup_logging(config)

        mock_basic_config.assert_called_once_with(
            level=logging.DEBUG, format="test format", filename=None, filemode=None
        )

    @patch("shadowlink.cli.logging.basicConfig")
    def test_setup_logging_with_file(self, mock_basic_config):
        """Test logging configuration with file output."""
        config = ShadowLinkConfig(log_level="INFO", log_file="test.log")

        setup_logging(config)

        mock_basic_config.assert_called_once_with(
            level=logging.INFO, format=config.log_format, filename="test.log", filemode="a"
        )

    @patch("shadowlink.cli.logging.basicConfig")
    @patch("shadowlink.cli.logger")
    def test_setup_logging_invalid_level(self, mock_logger, mock_basic_config):
        """Test logging with invalid level defaults to INFO."""
        config = ShadowLinkConfig(log_level="INVALID")

        setup_logging(config)

        mock_basic_config.assert_called_once_with(
            level=logging.INFO,  # Should default to INFO for invalid level
            format=config.log_format,
            filename=None,
            filemode=None,
        )


class TestCreateParser:
    """Test create_parser function."""

    def test_create_parser_basic(self):
        """Test basic parser creation."""
        parser = create_parser()

        assert isinstance(parser, argparse.ArgumentParser)
        assert parser.prog == "shadowlink"
        assert "Ultimate URL Cloaking Tool" in parser.description

    def test_create_parser_arguments(self):
        """Test parser has all required arguments."""
        parser = create_parser()

        # Test parsing valid arguments
        args = parser.parse_args(
            ["https://example.com", "-d", "facebook.com", "-k", "test", "-f", "json", "--no-banner"]
        )

        assert args.url == "https://example.com"
        assert args.domain == "facebook.com"
        assert args.keyword == "test"
        assert args.format == "json"
        assert args.no_banner is True

    def test_create_parser_optional_arguments(self):
        """Test parser with optional arguments."""
        parser = create_parser()

        args = parser.parse_args(
            ["--batch", "urls.txt", "--timeout", "30", "--max-retries", "5", "--log-level", "DEBUG"]
        )

        assert args.batch == Path("urls.txt")
        assert args.timeout == 30
        assert args.max_retries == 5
        assert args.log_level == "DEBUG"


class TestProcessSingleUrl:
    """Test process_single_url function."""

    def test_process_single_url_success(self):
        """Test successful URL processing."""
        config = ShadowLinkConfig()

        with (
            patch("shadowlink.cli.validate_url"),
            patch("shadowlink.cli.validate_domain"),
            patch("shadowlink.cli.validate_keyword"),
            patch(
                "shadowlink.cli.generate_masked_urls",
                return_value=["http://masked1.com", "http://masked2.com"],
            ),
        ):

            result = process_single_url("https://example.com", "facebook.com", "test", config)

            assert result["success"] is True
            assert result["original_url"] == "https://example.com"
            assert result["domain"] == "facebook.com"
            assert result["keyword"] == "test"
            assert len(result["masked_urls"]) == 2
            assert result["errors"] == []

    def test_process_single_url_validation_error(self):
        """Test URL processing with validation error."""
        config = ShadowLinkConfig()

        with patch(
            "shadowlink.cli.validate_url", side_effect=ValidationError("Invalid URL", "url", "test")
        ):

            result = process_single_url("invalid-url", "facebook.com", "test", config)

            assert result["success"] is False
            assert result["masked_urls"] == []
            assert len(result["errors"]) == 1
            assert "ValidationError" in result["errors"][0]

    def test_process_single_url_network_error(self):
        """Test URL processing with network error."""
        config = ShadowLinkConfig()

        with (
            patch("shadowlink.cli.validate_url"),
            patch("shadowlink.cli.validate_domain"),
            patch("shadowlink.cli.validate_keyword"),
            patch(
                "shadowlink.cli.generate_masked_urls", side_effect=NetworkError("Network failed")
            ),
        ):

            result = process_single_url("https://example.com", "facebook.com", "test", config)

            assert result["success"] is False
            assert "NetworkError" in result["errors"][0]

    def test_process_single_url_masking_error(self):
        """Test URL processing with masking error."""
        config = ShadowLinkConfig()

        with (
            patch("shadowlink.cli.validate_url"),
            patch("shadowlink.cli.validate_domain"),
            patch("shadowlink.cli.validate_keyword"),
            patch(
                "shadowlink.cli.generate_masked_urls", side_effect=MaskingError("Masking failed")
            ),
        ):

            result = process_single_url("https://example.com", "facebook.com", "test", config)

            assert result["success"] is False
            assert "MaskingError" in result["errors"][0]


class TestProcessBatchFile:
    """Test process_batch_file function."""

    def test_process_batch_file_success(self):
        """Test successful batch file processing."""
        config = ShadowLinkConfig()
        batch_content = "https://example1.com\nhttps://example2.com\n"

        with (
            patch("builtins.open", mock_open(read_data=batch_content)),
            patch("shadowlink.cli.process_single_url") as mock_process,
        ):

            mock_process.return_value = {"success": True, "masked_urls": ["test"]}

            results = process_batch_file(Path("test.txt"), "facebook.com", "test", config)

            assert len(results) == 2
            assert mock_process.call_count == 2

    def test_process_batch_file_not_found(self):
        """Test batch file processing with missing file."""
        config = ShadowLinkConfig()

        with patch("builtins.open", side_effect=FileNotFoundError()):
            with pytest.raises(FileNotFoundError):
                process_batch_file(Path("missing.txt"), "facebook.com", "test", config)

    def test_process_batch_file_empty_lines(self):
        """Test batch file processing with empty lines."""
        config = ShadowLinkConfig()
        batch_content = "https://example1.com\n\n  \nhttps://example2.com\n"

        with (
            patch("builtins.open", mock_open(read_data=batch_content)),
            patch("shadowlink.cli.process_single_url") as mock_process,
        ):

            mock_process.return_value = {"success": True}

            results = process_batch_file(Path("test.txt"), "facebook.com", "test", config)

            # Should only process non-empty lines
            assert mock_process.call_count == 2


class TestInteractiveMode:
    """Test interactive_mode function."""

    @patch("shadowlink.cli.show_banner")
    @patch("builtins.input")
    @patch("shadowlink.cli.process_single_url")
    def test_interactive_mode_success(self, mock_process, mock_input, mock_banner):
        """Test successful interactive mode."""
        config = ShadowLinkConfig(show_banner=True)
        mock_input.side_effect = ["https://example.com", "facebook.com", "test"]
        mock_process.return_value = {"success": True}

        with (
            patch("shadowlink.cli.validate_url"),
            patch("shadowlink.cli.validate_domain"),
            patch("shadowlink.cli.validate_keyword"),
        ):

            result = interactive_mode(config)

            mock_banner.assert_called_once()
            assert result["success"] is True

    @patch("shadowlink.cli.show_banner")
    @patch("builtins.input")
    def test_interactive_mode_no_banner(self, mock_input, mock_banner):
        """Test interactive mode without banner."""
        config = ShadowLinkConfig(show_banner=False)
        mock_input.side_effect = KeyboardInterrupt()

        result = interactive_mode(config)

        mock_banner.assert_not_called()
        assert result is None

    @patch("builtins.input")
    @patch("builtins.print")
    def test_interactive_mode_validation_retry(self, mock_print, mock_input):
        """Test interactive mode with validation errors and retry."""
        config = ShadowLinkConfig(show_banner=False)
        mock_input.side_effect = ["invalid", "https://example.com", "facebook.com", "test"]

        with (
            patch(
                "shadowlink.cli.validate_url",
                side_effect=[ValidationError("Invalid", "url", "invalid"), None],
            ),
            patch("shadowlink.cli.validate_domain"),
            patch("shadowlink.cli.validate_keyword"),
            patch("shadowlink.cli.process_single_url", return_value={"success": True}),
        ):

            result = interactive_mode(config)

            assert result["success"] is True
            # Should have printed error message
            mock_print.assert_any_call("✖ Invalid")

    @patch("builtins.input")
    @patch("builtins.print")
    def test_interactive_mode_keyboard_interrupt(self, mock_print, mock_input):
        """Test interactive mode with keyboard interrupt."""
        config = ShadowLinkConfig(show_banner=False)
        mock_input.side_effect = KeyboardInterrupt()

        result = interactive_mode(config)

        assert result is None
        mock_print.assert_called_with("\n✖ Cancelled by user")


class TestMainCli:
    """Test main_cli function."""

    @patch("shadowlink.cli.load_config")
    @patch("shadowlink.cli.setup_logging")
    @patch("shadowlink.cli.process_single_url")
    @patch("shadowlink.cli.OutputFormatter")
    @patch("sys.argv", ["shadowlink", "https://example.com", "-d", "facebook.com", "-k", "test"])
    def test_main_cli_command_line_mode(
        self, mock_formatter, mock_process, mock_setup, mock_load_config
    ):
        """Test main CLI in command line mode."""
        mock_config = ShadowLinkConfig()
        mock_load_config.return_value = mock_config
        mock_process.return_value = {"success": True}
        mock_formatter_instance = Mock()
        mock_formatter.return_value = mock_formatter_instance

        result = main_cli()

        assert result == 0
        mock_process.assert_called_once()
        mock_formatter_instance.output_results.assert_called_once()

    @patch("shadowlink.cli.load_config")
    @patch("shadowlink.cli.setup_logging")
    @patch("shadowlink.cli.interactive_mode")
    @patch("shadowlink.cli.OutputFormatter")
    @patch("sys.argv", ["shadowlink"])
    def test_main_cli_interactive_mode(
        self, mock_formatter, mock_interactive, mock_setup, mock_load_config
    ):
        """Test main CLI in interactive mode."""
        mock_config = ShadowLinkConfig()
        mock_load_config.return_value = mock_config
        mock_interactive.return_value = {"success": True}
        mock_formatter_instance = Mock()
        mock_formatter.return_value = mock_formatter_instance

        result = main_cli()

        assert result == 0
        mock_interactive.assert_called_once()

    @patch("shadowlink.cli.load_config")
    @patch("shadowlink.cli.setup_logging")
    @patch("shadowlink.cli.process_batch_file")
    @patch("shadowlink.cli.OutputFormatter")
    @patch("sys.argv", ["shadowlink", "--batch", "urls.txt", "-d", "facebook.com", "-k", "test"])
    def test_main_cli_batch_mode(self, mock_formatter, mock_batch, mock_setup, mock_load_config):
        """Test main CLI in batch mode."""
        mock_config = ShadowLinkConfig()
        mock_load_config.return_value = mock_config
        mock_batch.return_value = [{"success": True}]
        mock_formatter_instance = Mock()
        mock_formatter.return_value = mock_formatter_instance

        result = main_cli()

        assert result == 0
        mock_batch.assert_called_once()

    @patch("shadowlink.cli.load_config")
    @patch("shadowlink.cli.setup_logging")
    @patch("builtins.print")
    @patch("sys.argv", ["shadowlink", "--batch", "urls.txt"])
    def test_main_cli_batch_mode_missing_args(self, mock_print, mock_setup, mock_load_config):
        """Test main CLI batch mode with missing required arguments."""
        mock_config = ShadowLinkConfig()
        mock_load_config.return_value = mock_config

        result = main_cli()

        assert result == 1
        mock_print.assert_called_with("✖ Domain and keyword are required for batch processing")

    @patch("shadowlink.cli.ShadowLinkConfig.load_from_file")
    @patch("shadowlink.cli.setup_logging")
    @patch("sys.argv", ["shadowlink", "--config", "custom.json", "--save-config"])
    @patch("builtins.print")
    def test_main_cli_save_config(self, mock_print, mock_setup, mock_load_from_file):
        """Test main CLI save config functionality."""
        mock_config = ShadowLinkConfig()
        mock_config.get_config_dir = Mock(return_value=Path("/test"))
        mock_config.save_to_file = Mock()
        mock_load_from_file.return_value = mock_config

        result = main_cli()

        assert result == 0
        mock_config.save_to_file.assert_called_once()

    @patch("shadowlink.cli.load_config")
    @patch("shadowlink.cli.setup_logging")
    @patch("shadowlink.cli.logger")
    @patch("builtins.print")
    @patch("sys.argv", ["shadowlink"])
    def test_main_cli_unexpected_error(self, mock_print, mock_logger, mock_setup, mock_load_config):
        """Test main CLI with unexpected error."""
        mock_load_config.side_effect = Exception("Unexpected error")

        result = main_cli()

        assert result == 1
        mock_print.assert_called_with("✖ Unexpected error: Unexpected error")

    @patch("shadowlink.cli.load_config")
    @patch("shadowlink.cli.setup_logging")
    @patch("shadowlink.cli.process_single_url")
    @patch("shadowlink.cli.OutputFormatter")
    @patch("sys.argv", ["shadowlink", "https://example.com", "-d", "facebook.com", "-k", "test"])
    def test_main_cli_failed_processing(
        self, mock_formatter, mock_process, mock_setup, mock_load_config
    ):
        """Test main CLI with failed processing."""
        mock_config = ShadowLinkConfig()
        mock_load_config.return_value = mock_config
        mock_process.return_value = {"success": False}
        mock_formatter_instance = Mock()
        mock_formatter.return_value = mock_formatter_instance

        result = main_cli()

        assert result == 1
