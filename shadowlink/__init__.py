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

__all__: list[str] = [
    "main",
    "mask_url",
    "validate_url",
    "validate_domain",
    "validate_keyword",
    "__version__",
]
