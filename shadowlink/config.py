"""Configuration management for ShadowLink.

This module handles configuration loading from files, environment variables,
and provides default settings for production deployment.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)


@dataclass
class ShadowLinkConfig:
    """Configuration settings for ShadowLink application.

    This class holds all configurable settings including API limits,
    timeouts, output preferences, and service configurations.
    """

    # Input validation settings
    max_keyword_length: int = 15
    max_retries: int = 3

    # UI and display settings
    spinner_iterations: int = 12
    spinner_delay: float = 0.1
    show_banner: bool = True
    colored_output: bool = True

    # Network and API settings
    request_timeout: int = 10
    rate_limit_delay: float = 1.0
    max_concurrent_requests: int = 4

    # Output settings
    output_format: str = "console"  # console, json, csv, yaml
    should_save_to_file: bool = False
    output_file: Optional[str] = None

    # Service configuration
    enabled_services: List[str] = field(
        default_factory=lambda: ["tinyurl", "dagd", "clckru", "osdb"]
    )

    # Logging configuration
    log_level: str = "INFO"
    log_file: Optional[str] = None
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Cache settings
    enable_cache: bool = True
    cache_ttl: int = 3600  # 1 hour
    cache_size: int = 1000

    @classmethod
    def load_from_file(cls, config_path: Path) -> "ShadowLinkConfig":
        """Load configuration from a JSON file.

        Args:
            config_path: Path to the configuration file

        Returns:
            ShadowLinkConfig instance with loaded settings

        Raises:
            FileNotFoundError: If config file doesn't exist
            json.JSONDecodeError: If config file is invalid JSON
        """
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config_data = json.load(f)

            logger.info(f"Loaded configuration from {config_path}")
            return cls(**config_data)

        except FileNotFoundError:
            logger.warning(f"Config file not found: {config_path}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in config file: {e}")
            raise

    @classmethod
    def load_from_env(cls) -> "ShadowLinkConfig":
        """Load configuration from environment variables.

        Environment variables should be prefixed with SHADOWLINK_
        and use uppercase names (e.g., SHADOWLINK_MAX_RETRIES).

        Returns:
            ShadowLinkConfig instance with environment settings
        """
        config_data = {}
        env_prefix = "SHADOWLINK_"

        def safe_bool_converter(x):
            if x.lower() in ("true", "1", "yes", "on"):
                return True
            elif x.lower() in ("false", "0", "no", "off"):
                return False
            else:
                return None  # Invalid value, will be ignored

        # Map environment variables to config fields
        env_mappings = {
            "MAX_KEYWORD_LENGTH": ("max_keyword_length", int),
            "MAX_RETRIES": ("max_retries", int),
            "SPINNER_ITERATIONS": ("spinner_iterations", int),
            "SPINNER_DELAY": ("spinner_delay", float),
            "SHOW_BANNER": ("show_banner", safe_bool_converter),
            "COLORED_OUTPUT": ("colored_output", safe_bool_converter),
            "REQUEST_TIMEOUT": ("request_timeout", int),
            "RATE_LIMIT_DELAY": ("rate_limit_delay", float),
            "OUTPUT_FORMAT": ("output_format", str),
            "SAVE_TO_FILE": ("should_save_to_file", safe_bool_converter),
            "OUTPUT_FILE": ("output_file", str),
            "LOG_LEVEL": ("log_level", str),
            "LOG_FILE": ("log_file", str),
            "ENABLE_CACHE": ("enable_cache", safe_bool_converter),
            "CACHE_TTL": ("cache_ttl", int),
        }

        for env_key, (config_key, converter) in env_mappings.items():
            env_value = os.getenv(f"{env_prefix}{env_key}")
            if env_value is not None:
                try:
                    converted_value = converter(env_value)
                    if converted_value is not None:
                        config_data[config_key] = converted_value
                        logger.debug(f"Loaded {config_key} from environment: {env_value}")
                    elif converter == safe_bool_converter:
                        logger.warning(
                            f"Invalid environment value for {env_key}: {env_value} (invalid boolean)"
                        )
                except (ValueError, TypeError) as e:
                    logger.warning(f"Invalid environment value for {env_key}: {env_value} ({e})")

        return cls(**config_data)

    def save_to_file(self, config_path: Path) -> None:
        """Save current configuration to a JSON file.

        Args:
            config_path: Path where to save the configuration
        """
        config_dict = {
            key: value for key, value in self.__dict__.items() if not key.startswith("_")
        }

        try:
            config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(config_dict, f, indent=2, default=str)

            logger.info(f"Configuration saved to {config_path}")

        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")
            raise

    def get_config_dir(self) -> Path:
        """Get the user's configuration directory for ShadowLink.

        Returns:
            Path to the configuration directory
        """
        if os.name == "nt":  # Windows
            config_dir = Path(os.getenv("APPDATA", "~")) / "ShadowLink"
        else:  # Unix-like systems
            xdg_config = os.getenv("XDG_CONFIG_HOME")
            if xdg_config:
                config_dir = Path(str(xdg_config)) / "shadowlink"
            else:
                config_dir = Path(str(Path.home())) / ".config" / "shadowlink"

        return config_dir.expanduser()


def load_config() -> ShadowLinkConfig:
    """Load configuration from multiple sources with priority order.

    Priority order (highest to lowest):
    1. Environment variables
    2. User config file (~/.config/shadowlink/config.json)
    3. System config file (/etc/shadowlink/config.json)
    4. Default values

    Returns:
        ShadowLinkConfig instance with merged settings
    """
    # Start with default configuration
    config = ShadowLinkConfig()

    # Try to load from system config file
    system_config_path = Path("/etc/shadowlink/config.json")
    if system_config_path.exists():
        try:
            system_config = ShadowLinkConfig.load_from_file(system_config_path)
            defaults = ShadowLinkConfig()
            for key, value in system_config.__dict__.items():
                if not key.startswith("_") and hasattr(config, key):
                    default_value = getattr(defaults, key)
                    if value != default_value:
                        setattr(config, key, value)
            logger.info("Loaded system configuration")
        except Exception as e:
            logger.warning(f"Failed to load system config: {e}")

    # Try to load from user config file
    user_config_path = config.get_config_dir() / "config.json"
    if user_config_path.exists():
        try:
            user_config = ShadowLinkConfig.load_from_file(user_config_path)
            defaults = ShadowLinkConfig()
            for key, value in user_config.__dict__.items():
                if not key.startswith("_") and hasattr(config, key):
                    default_value = getattr(defaults, key)
                    if value != default_value:
                        setattr(config, key, value)
            logger.info("Loaded user configuration")
        except Exception as e:
            logger.warning(f"Failed to load user config: {e}")

    # Override with environment variables
    try:
        env_config = ShadowLinkConfig.load_from_env()
        defaults = ShadowLinkConfig()
        for key, value in env_config.__dict__.items():
            if not key.startswith("_") and hasattr(config, key):
                # Only set if the env value is different from default
                default_value = getattr(defaults, key)
                if value != default_value:
                    setattr(config, key, value)
        logger.info("Applied environment variable overrides")
    except Exception as e:
        logger.warning(f"Failed to load environment config: {e}")

    return config
