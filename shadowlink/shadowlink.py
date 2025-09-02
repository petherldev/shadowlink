#!/usr/bin/env python3

# ShadowLink
# Author: HErl (https://github.com/petherldev/shadowlink.git)
# License: MIT

"""ShadowLink – Ultimate URL Cloaking Tool (CLI implementation).

Run `shadowlink` from the shell or `python -m shadowlink` and follow the
interactive prompts to produce convincing, cloaked links that mask the
real destination behind a trusted‑looking domain.
"""

from __future__ import annotations

import logging
import re
import sys
import time
from typing import List, Match, Optional, Callable
from urllib.parse import urlparse

import pyshorteners

# Configuration constants
MAX_KEYWORD_LENGTH = 15
SPINNER_ITERATIONS = 12
SPINNER_DELAY = 0.1
MAX_RETRIES = 3

# Terminal colours (ANSI escape sequences)
RED = "\033[31m"
GRN = "\033[32m"
YLW = "\033[33m"
CYN = "\033[36m"
RST = "\033[0m"

# Project metadata – pulled from the package root
from .version import __version__ as VERSION  # noqa: E402  (after imports)

AUTHOR = "HErl"
GITHUB = "https://github.com/petherldev/shadowlink"

BANNER = r"""
███████ ██   ██  █████  ██████   ██████  ██     ██     ██      ██ ███    ██ ██   ██ 
██      ██   ██ ██   ██ ██   ██ ██    ██ ██     ██     ██      ██ ████   ██ ██  ██  
███████ ███████ ███████ ██   ██ ██    ██ ██  █  ██     ██      ██ ██ ██  ██ █████   
     ██ ██   ██ ██   ██ ██   ██ ██    ██ ██ ███ ██     ██      ██ ██  ██ ██ ██  ██  
███████ ██   ██ ██   ██ ██████   ██████   ███ ███      ███████ ██ ██   ████ ██   ██ 
                                                                                   
           ✪ ShadowLink – Ultimate URL Cloaking Tool ✪
"""

_URL_RE = re.compile(
    r"^https?://"  # Protocol
    r"(?:"
    r"(?:(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)*[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.?[a-zA-Z]{2,}(?::\d{1,5})?)|"  # Updated to handle complex subdomains with multiple dots and ports
    r"localhost(?::\d{1,5})?|"  # localhost with optional port
    r"(?:\d{1,3}\.){3}\d{1,3}(?::\d{1,5})?"  # IP address with optional port
    r")"
    r"(?:/[^\s]*)?"  # Optional path
    r"$",
    re.IGNORECASE,
)

_DOMAIN_RE = re.compile(
    r"^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)*"  # Subdomains
    r"[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?"  # Domain
    r"\.[a-zA-Z]{2,}$",  # TLD
    re.IGNORECASE,
)

from .exceptions import (
    ValidationError,
    URLShorteningError,
    MaskingError,
    NetworkError,
)

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def show_banner() -> None:
    """Print the stylised ASCII banner and project metadata.

    Displays the ShadowLink banner with version information, author details,
    and GitHub repository link in a formatted, colorized output.
    """
    print(f"{CYN}{BANNER}{RST}")
    print(f"{GRN}➤ Version      : {RST}{VERSION}")
    print(f"{GRN}➤ Author       : {RST}{AUTHOR}")
    print(f"{GRN}➤ GitHub       : {RST}{GITHUB}\n")


def loading_spinner(message: str = "generating your masked links") -> None:
    """Display an animated spinner while processing.

    Args:
        message: Custom message to display with the spinner

    Shows a rotating spinner animation to indicate background processing
    is occurring, particularly useful during network operations.
    """
    spinner = ["◐", "◓", "◑", "◒"]
    for _ in range(SPINNER_ITERATIONS):
        for frame in spinner:
            sys.stdout.write(f"\r{RED}⟳ Please wait... {message} {frame}{RST}")
            sys.stdout.flush()
            time.sleep(SPINNER_DELAY)
    sys.stdout.write("\r\033[K")  # Clear the line


def validate_url(url: str) -> Optional[Match[str]]:
    """Validate if the provided string is a syntactically correct HTTP(S) URL.

    Args:
        url: The URL string to validate

    Returns:
        A regex match object if valid, None otherwise

    Raises:
        ValidationError: If the URL format is invalid

    Validates URLs against a comprehensive regex pattern that checks for:
    - HTTP/HTTPS protocol
    - Valid domain structure
    - Optional port numbers
    - Optional paths and query parameters
    """
    if not url or not isinstance(url, str):
        raise ValidationError("URL must be a non-empty string", field="url", value=str(url))

    url = url.strip()
    if not url:
        raise ValidationError("URL cannot be empty or whitespace only", field="url", value=url)

    match = _URL_RE.match(url)
    if not match:
        raise ValidationError(
            "Invalid URL format. Must be a valid HTTP or HTTPS URL", field="url", value=url
        )

    return match


def validate_domain(domain: str) -> Optional[Match[str]]:
    """Validate if the provided string is a valid domain name.

    Args:
        domain: The domain string to validate

    Returns:
        A regex match object if valid, None otherwise

    Raises:
        ValidationError: If the domain format is invalid

    Validates domain names according to RFC standards, checking for:
    - Valid subdomain structure
    - Proper domain name format
    - Valid top-level domain
    """
    if not domain or not isinstance(domain, str):
        raise ValidationError(
            "Domain must be a non-empty string", field="domain", value=str(domain)
        )

    domain = domain.strip()
    if not domain:
        raise ValidationError(
            "Domain cannot be empty or whitespace only", field="domain", value=domain
        )

    # Check for common invalid patterns
    if domain.startswith(".") or domain.endswith("."):
        raise ValidationError("Domain cannot start or end with a dot", field="domain", value=domain)

    if ".." in domain:
        raise ValidationError(
            "Domain cannot contain consecutive dots", field="domain", value=domain
        )

    match = _DOMAIN_RE.match(domain)
    if not match:
        raise ValidationError(
            "Invalid domain format. Must be a valid domain name (e.g., example.com)",
            field="domain",
            value=domain,
        )

    return match


def validate_keyword(keyword: str) -> bool:
    """Validate if the keyword meets the requirements for URL masking.

    Args:
        keyword: The keyword string to validate

    Returns:
        True if valid

    Raises:
        ValidationError: If the keyword format is invalid

    Requirements:
    - Must not contain spaces or special characters
    - Must be between 1 and MAX_KEYWORD_LENGTH characters
    - Must contain only alphanumeric characters and hyphens
    """
    if keyword is None or not isinstance(keyword, str):
        raise ValidationError(
            "Keyword must be a non-empty string", field="keyword", value=str(keyword)
        )

    keyword = keyword.strip()
    if not keyword:
        raise ValidationError("Keyword cannot be empty", field="keyword", value=keyword)

    # Don't allow keywords that start or end with hyphens
    if keyword.startswith("-") or keyword.endswith("-"):
        raise ValidationError(
            "Keyword cannot start or end with a hyphen", field="keyword", value=keyword
        )

    # Check length constraints
    if len(keyword) > MAX_KEYWORD_LENGTH:
        raise ValidationError(
            f"Keyword must be {MAX_KEYWORD_LENGTH} characters or less",
            field="keyword",
            value=keyword,
        )

    # Check for invalid characters (only allow alphanumeric and hyphens)
    if not re.match(r"^[a-zA-Z0-9-]+$", keyword):
        raise ValidationError(
            "Keyword can only contain letters, numbers, and hyphens", field="keyword", value=keyword
        )

    return True


def mask_url(domain: str, keyword: str, short_url: str) -> str:
    """Create a masked URL by injecting domain and keyword into the short URL.

    Args:
        domain: The domain to use for masking
        keyword: The keyword to include in the masked URL
        short_url: The shortened URL to mask

    Returns:
        A masked URL string

    Raises:
        MaskingError: If any of the input parameters are invalid or masking fails

    Creates a convincing masked URL by embedding the fake domain and keyword
    into the structure of the shortened URL, making it appear to come from
    the specified domain.
    """
    if not all([domain, keyword, short_url]):
        raise MaskingError(
            "All parameters (domain, keyword, short_url) are required",
            domain=domain,
            keyword=keyword,
            url=short_url,
        )

    try:
        parsed = urlparse(short_url)
        if not parsed.scheme or not parsed.netloc:
            raise MaskingError(
                "Invalid short URL format - missing scheme or netloc",
                domain=domain,
                keyword=keyword,
                url=short_url,
            )

        masked = f"{parsed.scheme}://{domain}-{keyword}@{parsed.netloc}{parsed.path}"
        logger.info(f"Created masked URL: {masked}")
        return masked

    except Exception as e:
        logger.error(f"Error creating masked URL: {e}")
        raise MaskingError(
            f"Failed to create masked URL: {e}", domain=domain, keyword=keyword, url=short_url
        )


def get_user_input(prompt: str, validator: Callable[[str], bool], error_msg: str) -> str:
    """Get validated user input with retry logic.

    Args:
        prompt: The input prompt to display
        validator: Function to validate the input
        error_msg: Error message to show for invalid input

    Returns:
        Valid user input string

    Raises:
        ValidationError: If maximum retry attempts are exceeded
        KeyboardInterrupt: If user interrupts input

    Continuously prompts the user until valid input is provided,
    with clear error messages for invalid attempts.
    """
    attempts = 0
    while attempts < MAX_RETRIES:
        try:
            user_input = input(prompt).strip()
            if validator(user_input):
                return user_input
        except ValidationError as ve:
            print(f"{RED}✖ {ve.message}{RST}")
        except (EOFError, KeyboardInterrupt):
            raise KeyboardInterrupt("User interrupted input")
        except Exception as e:
            print(f"{RED}✖ {error_msg}: {e}{RST}")

        attempts += 1
        if attempts < MAX_RETRIES:
            print(f"{YLW}➤ Please try again ({MAX_RETRIES - attempts} attempts remaining){RST}")

    raise ValidationError(f"Maximum retry attempts ({MAX_RETRIES}) exceeded")


def generate_masked_urls(target_url: str, domain: str, keyword: str) -> List[str]:
    """Generate multiple masked URLs using different shortening services.

    Args:
        target_url: The original URL to shorten and mask
        domain: The domain to use for masking
        keyword: The keyword to include in masked URLs

    Returns:
        List of successfully generated masked URLs

    Raises:
        NetworkError: If all shortening services fail

    Attempts to create shortened URLs using multiple services and masks
    each successful result. Handles service failures gracefully.
    """
    shortener = pyshorteners.Shortener()
    services = [
        ("TinyURL", shortener.tinyurl),
        ("Da.gd", shortener.dagd),
        ("Clck.ru", shortener.clckru),
        ("OSDB", shortener.osdb),
    ]

    masked_urls = []
    service_errors = []

    for service_name, service in services:
        try:
            logger.info(f"Attempting to shorten URL with {service_name}")
            short_url = service.short(target_url)
            masked = mask_url(domain, keyword, short_url)
            masked_urls.append(masked)
            logger.info(f"Successfully created masked URL with {service_name}")
        except Exception as exc:
            error_msg = f"Failed with {service_name}: {exc}"
            service_errors.append(error_msg)
            logger.warning(error_msg)
            print(f"{RED}✖ {error_msg}{RST}")

    if not masked_urls:
        raise NetworkError(
            f"All URL shortening services failed. Errors: {'; '.join(service_errors)}"
        )

    return masked_urls


def main() -> None:
    """Interactive command-line interface entry point.

    Provides a user-friendly CLI for creating masked URLs through an
    interactive process that guides users through each step:
    1. Input validation for target URL
    2. Domain selection for masking
    3. Keyword selection
    4. URL generation and display

    Handles user interruption and errors gracefully with appropriate
    error messages and logging.
    """
    try:
        show_banner()
        logger.info("ShadowLink CLI started")

        # Get and validate target URL
        target_url = get_user_input(
            f"{YLW}➤ Paste the original link to cloak {RST}(e.g. https://example.com): {RST}",
            lambda url: validate_url(url) is not None,
            "Invalid URL format",
        )

        # Get and validate custom domain
        custom_domain = get_user_input(
            f"{YLW}➤ Enter a domain to disguise as {RST}(e.g. x.com): {RST}",
            lambda domain: validate_domain(domain) is not None,
            "Invalid domain format",
        )

        # Get and validate keyword
        keyword = get_user_input(
            f"{YLW}➤ Choose a keyword to add (e.g. login, signup, verify): {RST}",
            validate_keyword,
            "Invalid keyword format",
        )

        # Generate masked URLs
        loading_spinner()

        print(f"\n{CYN}➤ Original URL:{RST} {target_url}\n")

        masked_urls = generate_masked_urls(target_url, custom_domain, keyword)

        print(f"{GRN}[✓] Successfully generated {len(masked_urls)} masked URL(s):\n{RST}")
        for idx, masked_url in enumerate(masked_urls, start=1):
            print(f"{CYN}➤ Link {idx}:{RST} {masked_url}")
        logger.info(f"Successfully generated {len(masked_urls)} masked URLs")

    except KeyboardInterrupt:
        print(f"\n{RED}✖ Interrupted by user. Exiting...{RST}")
        logger.info("Application interrupted by user")
        sys.exit(1)
    except ValidationError as ve:
        print(f"{RED}✖ Validation error: {ve.message}{RST}")
        if ve.field and ve.value:
            logger.error(f"Validation failed for {ve.field}: {ve.value}")
        sys.exit(1)
    except NetworkError as ne:
        print(f"{RED}✖ Network error: {ne.message}{RST}")
        logger.error(f"Network error: {ne.message}")
        sys.exit(1)
    except MaskingError as me:
        print(f"{RED}✖ URL masking error: {me.message}{RST}")
        logger.error(f"Masking error: {me.message}")
        sys.exit(1)
    except Exception as exc:
        print(f"{RED}✖ Unexpected error: {exc}{RST}")
        logger.error(f"Unexpected error: {exc}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":  # pragma: no cover
    main()
