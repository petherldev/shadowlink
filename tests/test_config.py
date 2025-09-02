"""Comprehensive tests for configuration module functions."""

import json
import os
import tempfile
from pathlib import Path
from unittest.mock import patch, mock_open, Mock
import pytest

from shadowlink.config import ShadowLinkConfig, load_config


class TestShadowLinkConfig:
    """Test ShadowLinkConfig class methods."""

    def test_config_defaults(self):
        """Test default configuration values."""
        config = ShadowLinkConfig()

        assert config.max_keyword_length == 15
        assert config.max_retries == 3
        assert config.spinner_iterations == 12
        assert config.spinner_delay == 0.1
        assert config.show_banner is True
        assert config.colored_output is True
        assert config.request_timeout == 10
        assert config.output_format == "console"
        assert config.should_save_to_file is False
        assert config.output_file is None
        assert config.enabled_services == ["tinyurl", "dagd", "clckru", "osdb"]
        assert config.log_level == "INFO"
        assert config.enable_cache is True

    def test_load_from_file_success(self):
        """Test successful loading from file."""
        config_data = {"max_keyword_length": 20, "show_banner": False, "output_format": "json"}
        config_json = json.dumps(config_data)

        with patch("builtins.open", mock_open(read_data=config_json)):
            config = ShadowLinkConfig.load_from_file(Path("test.json"))

            assert config.max_keyword_length == 20
            assert config.show_banner is False
            assert config.output_format == "json"
            # Default values should still be present
            assert config.max_retries == 3

    def test_load_from_file_not_found(self):
        """Test loading from non-existent file."""
        with patch("builtins.open", side_effect=FileNotFoundError()):
            with pytest.raises(FileNotFoundError):
                ShadowLinkConfig.load_from_file(Path("missing.json"))

    def test_load_from_file_invalid_json(self):
        """Test loading from file with invalid JSON."""
        with patch("builtins.open", mock_open(read_data="invalid json")):
            with pytest.raises(json.JSONDecodeError):
                ShadowLinkConfig.load_from_file(Path("invalid.json"))

    def test_load_from_env_success(self):
        """Test successful loading from environment variables."""
        env_vars = {
            "SHADOWLINK_MAX_KEYWORD_LENGTH": "25",
            "SHADOWLINK_MAX_RETRIES": "5",
            "SHADOWLINK_SHOW_BANNER": "false",
            "SHADOWLINK_COLORED_OUTPUT": "true",
            "SHADOWLINK_REQUEST_TIMEOUT": "30",
            "SHADOWLINK_SPINNER_DELAY": "0.2",
            "SHADOWLINK_OUTPUT_FORMAT": "json",
            "SHADOWLINK_SAVE_TO_FILE": "true",
            "SHADOWLINK_OUTPUT_FILE": "output.json",
            "SHADOWLINK_LOG_LEVEL": "DEBUG",
            "SHADOWLINK_LOG_FILE": "app.log",
            "SHADOWLINK_ENABLE_CACHE": "false",
            "SHADOWLINK_CACHE_TTL": "7200",
        }

        with patch.dict(os.environ, env_vars):
            config = ShadowLinkConfig.load_from_env()

            assert config.max_keyword_length == 25
            assert config.max_retries == 5
            assert config.show_banner is False
            assert config.colored_output is True
            assert config.request_timeout == 30
            assert config.spinner_delay == 0.2
            assert config.output_format == "json"
            assert config.should_save_to_file is True
            assert config.output_file == "output.json"
            assert config.log_level == "DEBUG"
            assert config.log_file == "app.log"
            assert config.enable_cache is False
            assert config.cache_ttl == 7200

    def test_load_from_env_invalid_values(self):
        """Test loading from environment with invalid values."""
        env_vars = {
            "SHADOWLINK_MAX_RETRIES": "invalid",
            "SHADOWLINK_SPINNER_DELAY": "not_a_float",
            "SHADOWLINK_SHOW_BANNER": "maybe",
        }

        with patch.dict(os.environ, env_vars):
            config = ShadowLinkConfig.load_from_env()

            # Should use defaults for invalid values
            assert config.max_retries == 3  # default
            assert config.spinner_delay == 0.1  # default
            assert config.show_banner is True  # default

    def test_load_from_env_no_vars(self):
        """Test loading from environment with no relevant variables."""
        with patch.dict(os.environ, {}, clear=True):
            config = ShadowLinkConfig.load_from_env()

            # Should have all default values
            assert config.max_keyword_length == 15
            assert config.show_banner is True

    def test_save_to_file_success(self):
        """Test successful saving to file."""
        config = ShadowLinkConfig(max_keyword_length=20, output_format="json")

        with (
            patch("builtins.open", mock_open()) as mock_file,
            patch("pathlib.Path.mkdir") as mock_mkdir,
        ):

            config.save_to_file(Path("test.json"))

            mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)
            mock_file.assert_called_once_with(Path("test.json"), "w", encoding="utf-8")

            # Check that JSON was written
            handle = mock_file()
            written_data = "".join(call.args[0] for call in handle.write.call_args_list)
            saved_config = json.loads(written_data)

            assert saved_config["max_keyword_length"] == 20
            assert saved_config["output_format"] == "json"

    def test_save_to_file_error(self):
        """Test saving to file with error."""
        config = ShadowLinkConfig()

        with patch("builtins.open", side_effect=PermissionError("Access denied")):
            with pytest.raises(PermissionError):
                config.save_to_file(Path("test.json"))

    @patch("os.name", "nt")
    @patch("os.getenv")
    def test_get_config_dir_windows(self, mock_getenv):
        """Test get_config_dir on Windows."""
        mock_getenv.return_value = "C:\\Users\\Test\\AppData\\Roaming"
        config = ShadowLinkConfig()

        config_dir = config.get_config_dir()

        assert "ShadowLink" in str(config_dir)

    @patch("os.name", "posix")
    @patch("os.getenv")
    @patch("pathlib.Path.home")
    def test_get_config_dir_unix(self, mock_home, mock_getenv):
        """Test get_config_dir on Unix-like systems."""
        # Use string path to avoid PosixPath instantiation on Windows
        mock_home.return_value = "/home/user"
        mock_getenv.side_effect = lambda key, default=None: {
            "XDG_CONFIG_HOME": None,
        }.get(key, default)

        config = ShadowLinkConfig()

        with patch("pathlib.Path.__truediv__", return_value=Path("/home/user/.config/shadowlink")):
            config_dir = config.get_config_dir()

            assert "shadowlink" in str(config_dir)

    @patch("os.name", "posix")
    @patch("os.getenv")
    @patch("pathlib.Path.home")
    def test_get_config_dir_xdg_config_home(self, mock_home, mock_getenv):
        """Test get_config_dir with XDG_CONFIG_HOME set."""
        # Use string path to avoid PosixPath instantiation on Windows
        mock_home.return_value = "/home/user"
        mock_getenv.side_effect = lambda key, default=None: {
            "XDG_CONFIG_HOME": "/custom/config",
        }.get(key, default)

        config = ShadowLinkConfig()

        with patch("pathlib.Path.__truediv__", return_value=Path("/custom/config/shadowlink")):
            config_dir = config.get_config_dir()

            assert "/custom/config/shadowlink" in str(config_dir)


class TestLoadConfig:
    """Test load_config function."""

    @patch("shadowlink.config.ShadowLinkConfig.load_from_env")
    @patch("shadowlink.config.ShadowLinkConfig.load_from_file")
    @patch("pathlib.Path.exists")
    def test_load_config_all_sources(self, mock_exists, mock_load_file, mock_load_env):
        """Test loading config from all sources."""
        # Mock file existence
        mock_exists.side_effect = lambda: True

        system_config = ShadowLinkConfig(max_keyword_length=25, max_retries=8)
        user_config = ShadowLinkConfig(max_retries=5, show_banner=False)
        env_config = ShadowLinkConfig(show_banner=False, max_retries=7)

        mock_load_file.side_effect = [system_config, user_config]
        mock_load_env.return_value = env_config

        with patch.object(
            ShadowLinkConfig, "get_config_dir", return_value=Path("/home/user/.config/shadowlink")
        ):
            config = load_config()

            # Should have values from all sources with proper priority
            assert config.max_keyword_length == 25  # from system
            assert config.max_retries == 7  # from env (highest priority, overrides user config)
            assert config.show_banner is False  # from env (highest priority)

    @patch("shadowlink.config.ShadowLinkConfig.load_from_env")
    @patch("shadowlink.config.ShadowLinkConfig.load_from_file")
    @patch("pathlib.Path.exists")
    def test_load_config_no_files(self, mock_exists, mock_load_file, mock_load_env):
        """Test loading config with no config files."""
        mock_exists.return_value = False
        mock_load_env.return_value = ShadowLinkConfig()

        config = load_config()

        # Should have default values
        assert config.max_keyword_length == 15
        assert config.show_banner is True
        mock_load_file.assert_not_called()

    @patch("shadowlink.config.ShadowLinkConfig.load_from_env")
    @patch("shadowlink.config.ShadowLinkConfig.load_from_file")
    @patch("pathlib.Path.exists")
    def test_load_config_file_errors(self, mock_exists, mock_load_file, mock_load_env):
        """Test loading config with file errors."""
        mock_exists.return_value = True
        mock_load_file.side_effect = [Exception("File error"), Exception("Another error")]
        mock_load_env.return_value = ShadowLinkConfig(show_banner=False)

        with patch.object(
            ShadowLinkConfig, "get_config_dir", return_value=Path("/home/user/.config/shadowlink")
        ):
            config = load_config()

            # Should still work with defaults and env config
            assert config.show_banner is False  # from env
            assert config.max_keyword_length == 15  # default

    @patch("shadowlink.config.ShadowLinkConfig.load_from_env")
    @patch("pathlib.Path.exists")
    def test_load_config_env_error(self, mock_exists, mock_load_env):
        """Test loading config with environment error."""
        mock_exists.return_value = False
        mock_load_env.side_effect = Exception("Env error")

        config = load_config()

        # Should still work with defaults
        assert config.max_keyword_length == 15
        assert config.show_banner is True

    @patch("shadowlink.config.ShadowLinkConfig.load_from_env")
    @patch("shadowlink.config.ShadowLinkConfig.load_from_file")
    @patch("pathlib.Path.exists")
    def test_load_config_priority_order(self, mock_exists, mock_load_file, mock_load_env):
        """Test config loading priority order."""
        mock_exists.return_value = True  # Both system and user config files exist

        system_config = ShadowLinkConfig(max_keyword_length=30, max_retries=10)
        user_config = ShadowLinkConfig()  # default user config
        env_config = ShadowLinkConfig(max_retries=7)

        mock_load_file.side_effect = [system_config, user_config]
        mock_load_env.return_value = env_config

        with patch.object(
            ShadowLinkConfig,
            "get_config_dir",
            return_value=Path("/home/user/.config/shadowlink"),
        ):
            config = load_config()

            assert config.max_keyword_length == 30  # from system (not overridden)
            assert config.max_retries == 7  # from env (overridden)
