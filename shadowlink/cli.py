"""Enhanced CLI interface with argument parsing and production features.

This module provides a comprehensive command-line interface with support for
configuration files, different output formats, and advanced options.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Optional, List, Dict, Any
import logging

from .config import load_config, ShadowLinkConfig
from .shadowlink import (
    validate_url,
    validate_domain,
    validate_keyword,
    generate_masked_urls,
    show_banner,
)
from .exceptions import ValidationError, NetworkError, MaskingError
from .output import OutputFormatter
from .version import __version__

logger = logging.getLogger(__name__)


def setup_logging(config: ShadowLinkConfig) -> None:
    """Configure logging based on configuration settings.

    Args:
        config: Configuration object with logging settings
    """
    log_level = getattr(logging, config.log_level.upper(), logging.INFO)

    # Configure root logger
    logging.basicConfig(
        level=log_level,
        format=config.log_format,
        filename=config.log_file,
        filemode="a" if config.log_file else None,
    )

    # Set specific logger levels
    logging.getLogger("shadowlink").setLevel(log_level)

    if config.log_file:
        logger.info(f"Logging to file: {config.log_file}")


def create_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser.

    Returns:
        Configured ArgumentParser instance
    """
    parser = argparse.ArgumentParser(
        prog="shadowlink",
        description="Ultimate URL Cloaking Tool - mask URLs behind trusted domains",
        epilog="For more information, visit: https://github.com/petherldev/shadowlink",
    )

    parser.add_argument("--version", action="version", version=f"ShadowLink {__version__}")

    # Input arguments
    parser.add_argument(
        "url", nargs="?", help="URL to cloak (if not provided, interactive mode is used)"
    )

    parser.add_argument("-d", "--domain", help="Domain to disguise as (e.g., facebook.com)")

    parser.add_argument("-k", "--keyword", help="Keyword to add to the masked URL")

    # Output options
    parser.add_argument(
        "-f",
        "--format",
        choices=["console", "json", "csv", "yaml"],
        default="console",
        help="Output format (default: console)",
    )

    parser.add_argument("-o", "--output", help="Save output to file")

    parser.add_argument("--no-banner", action="store_true", help="Disable banner display")

    parser.add_argument("--no-color", action="store_true", help="Disable colored output")

    # Service options
    parser.add_argument(
        "--services",
        nargs="+",
        choices=["tinyurl", "dagd", "clckru", "osdb"],
        help="Specify which shortening services to use",
    )

    parser.add_argument("--timeout", type=int, help="Request timeout in seconds")

    # Configuration options
    parser.add_argument("--config", type=Path, help="Path to configuration file")

    parser.add_argument(
        "--save-config", action="store_true", help="Save current settings to user config file"
    )

    # Logging options
    parser.add_argument(
        "--log-level", choices=["DEBUG", "INFO", "WARNING", "ERROR"], help="Set logging level"
    )

    parser.add_argument("--log-file", help="Log to file instead of console")

    # Advanced options
    parser.add_argument("--batch", type=Path, help="Process URLs from a file (one URL per line)")

    parser.add_argument(
        "--max-retries", type=int, help="Maximum number of retries for failed requests"
    )

    return parser


def process_single_url(
    url: str, domain: str, keyword: str, config: ShadowLinkConfig
) -> Dict[str, Any]:
    """Process a single URL and return results.

    Args:
        url: URL to process
        domain: Domain for masking
        keyword: Keyword for masking
        config: Configuration object

    Returns:
        Dictionary with processing results
    """
    result = {
        "original_url": url,
        "domain": domain,
        "keyword": keyword,
        "masked_urls": [],
        "errors": [],
        "success": False,
    }

    try:
        # Validate inputs
        validate_url(url)
        validate_domain(domain)
        validate_keyword(keyword)

        # Generate masked URLs
        masked_urls = generate_masked_urls(url, domain, keyword)
        result["masked_urls"] = masked_urls
        result["success"] = True

        logger.info(f"Successfully processed URL: {url}")

    except (ValidationError, NetworkError, MaskingError) as e:
        error_msg = f"{type(e).__name__}: {e}"
        result["errors"].append(error_msg)
        logger.error(f"Failed to process URL {url}: {error_msg}")

    return result


def process_batch_file(
    batch_file: Path, domain: str, keyword: str, config: ShadowLinkConfig
) -> List[Dict[str, Any]]:
    """Process URLs from a batch file.

    Args:
        batch_file: Path to file containing URLs
        domain: Domain for masking
        keyword: Keyword for masking
        config: Configuration object

    Returns:
        List of processing results
    """
    results = []

    try:
        with open(batch_file, "r", encoding="utf-8") as f:
            urls = [line.strip() for line in f if line.strip()]

        logger.info(f"Processing {len(urls)} URLs from batch file")

        for i, url in enumerate(urls, 1):
            logger.info(f"Processing URL {i}/{len(urls)}: {url}")
            result = process_single_url(url, domain, keyword, config)
            results.append(result)

    except FileNotFoundError:
        logger.error(f"Batch file not found: {batch_file}")
        raise
    except Exception as e:
        logger.error(f"Error processing batch file: {e}")
        raise

    return results


def interactive_mode(config: ShadowLinkConfig) -> Optional[Dict[str, Any]]:
    """Run in interactive mode to get user input.

    Args:
        config: Configuration object

    Returns:
        Processing result or None if cancelled
    """
    try:
        if config.show_banner:
            show_banner()

        # Get URL
        while True:
            url = input("➤ Enter the URL to cloak: ").strip()
            if not url:
                continue
            try:
                validate_url(url)
                break
            except ValidationError as e:
                print(f"✖ {e.message}")

        # Get domain
        while True:
            domain = input("➤ Enter domain to disguise as: ").strip()
            if not domain:
                continue
            try:
                validate_domain(domain)
                break
            except ValidationError as e:
                print(f"✖ {e.message}")

        # Get keyword
        while True:
            keyword = input("➤ Enter keyword: ").strip()
            if not keyword:
                continue
            try:
                validate_keyword(keyword)
                break
            except ValidationError as e:
                print(f"✖ {e.message}")

        return process_single_url(url, domain, keyword, config)

    except KeyboardInterrupt:
        print("\n✖ Cancelled by user")
        return None


def main_cli() -> int:
    """Main CLI entry point with argument parsing.

    Returns:
        Exit code (0 for success, 1 for error)
    """
    parser = create_parser()
    args = parser.parse_args()

    try:
        # Load configuration
        if args.config:
            config = ShadowLinkConfig.load_from_file(args.config)
        else:
            config = load_config()

        # Override config with command line arguments
        if args.format:
            config.output_format = args.format
        if args.output:
            config.output_file = args.output
            config.save_to_file = True
        if args.no_banner:
            config.show_banner = False
        if args.no_color:
            config.colored_output = False
        if args.services:
            config.enabled_services = args.services
        if args.timeout:
            config.request_timeout = args.timeout
        if args.log_level:
            config.log_level = args.log_level
        if args.log_file:
            config.log_file = args.log_file
        if args.max_retries:
            config.max_retries = args.max_retries

        # Setup logging
        setup_logging(config)

        # Save configuration if requested
        if args.save_config:
            config_path = config.get_config_dir() / "config.json"
            config.save_to_file(config_path)
            print(f"Configuration saved to {config_path}")
            return 0

        # Process URLs
        results = []

        if args.batch:
            # Batch processing mode
            if not args.domain or not args.keyword:
                print("✖ Domain and keyword are required for batch processing")
                return 1

            results = process_batch_file(args.batch, args.domain, args.keyword, config)

        elif args.url and args.domain and args.keyword:
            # Command line mode
            result = process_single_url(args.url, args.domain, args.keyword, config)
            results = [result]

        else:
            # Interactive mode
            result = interactive_mode(config)
            if result:
                results = [result]

        # Format and output results
        if results:
            formatter = OutputFormatter(config)
            formatter.output_results(results)

        # Return appropriate exit code
        if results and all(r["success"] for r in results):
            return 0
        else:
            return 1

    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        print(f"✖ Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main_cli())
