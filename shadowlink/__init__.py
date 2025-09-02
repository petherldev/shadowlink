"""ShadowLink – Ultimate URL Cloaking Tool (package interface).

This module exposes the public API and makes the CLI available as
`python -m shadowlink` *or* the `shadowlink` console‑script installed via
`pip install shadowlink`.
"""

from __future__ import annotations
from .shadowlink import (
    main,
    mask_url,
    validate_url,
    validate_domain,
    validate_keyword,
)
from .version import __version__
from .exceptions import (
    ShadowLinkError,
    ValidationError,
    URLShorteningError,
    MaskingError,
    NetworkError,
    ConfigurationError,
)
from .config import ShadowLinkConfig, load_config
from .cli import main_cli
from .output import OutputFormatter

__all__: list[str] = [
    "main",
    "mask_url",
    "validate_url",
    "validate_domain",
    "validate_keyword",
    "__version__",
    "ShadowLinkError",
    "ValidationError",
    "URLShorteningError",
    "MaskingError",
    "NetworkError",
    "ConfigurationError",
    "ShadowLinkConfig",
    "load_config",
    "main_cli",
    "OutputFormatter",
]
