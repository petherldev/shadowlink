# ShadowLink API Documentation

This document provides comprehensive API documentation for the ShadowLink Python package.

## Table of Contents

- [Core Functions](#core-functions)
- [Configuration](#configuration)
- [Exceptions](#exceptions)
- [CLI Interface](#cli-interface)
- [Output Formatting](#output-formatting)
- [Examples](#examples)

## Core Functions

### `validate_url(url: str) -> Optional[Match[str]]`

Validates if the provided string is a syntactically correct HTTP(S) URL.

**Parameters:**
- `url` (str): The URL string to validate

**Returns:**
- `Optional[Match[str]]`: A regex match object if valid, None otherwise

**Raises:**
- `ValidationError`: If the URL format is invalid

**Example:**
```python
from shadowlink import validate_url

try:
    match = validate_url("https://example.com")
    if match:
        print("Valid URL")
except ValidationError as e:
    print(f"Invalid URL: {e.message}")
```

### `validate_domain(domain: str) -> Optional[Match[str]]`

Validates if the provided string is a valid domain name.

**Parameters:**
- `domain` (str): The domain string to validate

**Returns:**
- `Optional[Match[str]]`: A regex match object if valid, None otherwise

**Raises:**
- `ValidationError`: If the domain format is invalid

**Example:**
```python
from shadowlink import validate_domain

try:
    match = validate_domain("facebook.com")
    if match:
        print("Valid domain")
except ValidationError as e:
    print(f"Invalid domain: {e.message}")
```

### `validate_keyword(keyword: str) -> bool`

Validates if the keyword meets the requirements for URL masking.

**Parameters:**
- `keyword` (str): The keyword string to validate

**Returns:**
- `bool`: True if valid

**Raises:**
- `ValidationError`: If the keyword format is invalid

**Requirements:**
- Must be 1-15 characters long
- Can only contain letters, numbers, and hyphens
- Cannot start or end with hyphens

**Example:**
```python
from shadowlink import validate_keyword

try:
    if validate_keyword("login"):
        print("Valid keyword")
except ValidationError as e:
    print(f"Invalid keyword: {e.message}")
```

### `mask_url(domain: str, keyword: str, short_url: str) -> str`

Creates a masked URL by injecting domain and keyword into the short URL.

**Parameters:**
- `domain` (str): The domain to use for masking
- `keyword` (str): The keyword to include in the masked URL
- `short_url` (str): The shortened URL to mask

**Returns:**
- `str`: A masked URL string

**Raises:**
- `MaskingError`: If any parameters are invalid or masking fails

**Example:**
```python
from shadowlink import mask_url

try:
    masked = mask_url("facebook.com", "login", "https://tinyurl.com/abc123")
    print(f"Masked URL: {masked}")
    # Output: https://facebook.com-login@tinyurl.com/abc123
except MaskingError as e:
    print(f"Masking failed: {e.message}")
```

### `generate_masked_urls(target_url: str, domain: str, keyword: str) -> List[str]`

Generates multiple masked URLs using different shortening services.

**Parameters:**
- `target_url` (str): The original URL to shorten and mask
- `domain` (str): The domain to use for masking
- `keyword` (str): The keyword to include in masked URLs

**Returns:**
- `List[str]`: List of successfully generated masked URLs

**Raises:**
- `NetworkError`: If all shortening services fail
- `ValidationError`: If input parameters are invalid
- `MaskingError`: If URL masking fails

**Services Used:**
- TinyURL
- Da.gd
- Clck.ru
- OSDB

**Example:**
```python
from shadowlink import generate_masked_urls

try:
    masked_urls = generate_masked_urls(
        "https://example.com/long/path",
        "facebook.com",
        "login"
    )
    
    for i, url in enumerate(masked_urls, 1):
        print(f"Link {i}: {url}")
        
except (NetworkError, ValidationError, MaskingError) as e:
    print(f"Error: {e.message}")
```

### `show_banner() -> None`

Prints the stylized ASCII banner and project metadata.

**Example:**
```python
from shadowlink import show_banner

show_banner()
# Displays ShadowLink banner with version info
```

### `loading_spinner(message: str = "generating your masked links") -> None`

Displays an animated spinner while processing.

**Parameters:**
- `message` (str, optional): Custom message to display with the spinner

**Example:**
```python
from shadowlink import loading_spinner

loading_spinner("Processing your request")
```

## Configuration

### `ShadowLinkConfig`

Configuration class that holds all application settings.

**Attributes:**
```python
@dataclass
class ShadowLinkConfig:
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
    enabled_services: List[str] = ["tinyurl", "dagd", "clckru", "osdb"]
    
    # Logging configuration
    log_level: str = "INFO"
    log_file: Optional[str] = None
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Cache settings
    enable_cache: bool = True
    cache_ttl: int = 3600  # 1 hour
    cache_size: int = 1000
```

**Methods:**

#### `load_from_file(config_path: Path) -> ShadowLinkConfig`

Load configuration from a JSON file.

#### `load_from_env() -> ShadowLinkConfig`

Load configuration from environment variables (prefixed with `SHADOWLINK_`).

#### `save_to_file(config_path: Path) -> None`

Save current configuration to a JSON file.

#### `get_config_dir() -> Path`

Get the user's configuration directory for ShadowLink.

### `load_config() -> ShadowLinkConfig`

Loads configuration from multiple sources with priority order.

**Returns:**
- `ShadowLinkConfig`: Configuration instance with merged settings

**Priority Order:**
1. Environment variables (highest)
2. User config file (`~/.config/shadowlink/config.json`)
3. System config file (`/etc/shadowlink/config.json`)
4. Default values (lowest)

**Example:**
```python
from shadowlink import load_config

config = load_config()
print(f"Max retries: {config.max_retries}")
print(f"Output format: {config.output_format}")
```

## Exceptions

### Exception Hierarchy

```
ShadowLinkError (base)
├── ValidationError
├── URLShorteningError
├── MaskingError
├── NetworkError
└── ConfigurationError
```

### `ShadowLinkError`

Base exception class for all ShadowLink-related errors.

### `ValidationError`

Raised when input validation fails.

**Attributes:**
- `message` (str): Error message
- `field` (str): Field that failed validation
- `value` (str): Invalid value provided

**Example:**
```python
from shadowlink.exceptions import ValidationError

try:
    validate_url("invalid-url")
except ValidationError as e:
    print(f"Field: {e.field}")
    print(f"Value: {e.value}")
    print(f"Message: {e.message}")
```

### `URLShorteningError`

Raised when URL shortening operations fail.

**Attributes:**
- `message` (str): Error message
- `service` (str): Service that failed
- `original_error` (Exception): Underlying exception

### `MaskingError`

Raised when URL masking operations fail.

**Attributes:**
- `message` (str): Error message
- `domain` (str): Domain used for masking
- `keyword` (str): Keyword used for masking
- `url` (str): URL being masked

### `NetworkError`

Raised when network operations fail.

**Attributes:**
- `message` (str): Error message
- `service` (str): Service that couldn't be reached
- `status_code` (int): HTTP status code if applicable

### `ConfigurationError`

Raised when configuration issues are detected.

**Attributes:**
- `message` (str): Error message
- `config_key` (str): Configuration key that caused the issue

## CLI Interface

### `main() -> None`

Interactive command-line interface entry point. Provides a user-friendly CLI for creating masked URLs through guided prompts.

**Features:**
- Input validation for target URL
- Domain selection for masking
- Keyword selection
- URL generation and display
- Error handling with retry logic

**Example:**
```python
from shadowlink import main

# Run interactive CLI
main()
```

### `main_cli() -> int`

Enhanced CLI entry point with argument parsing and advanced features.

**Returns:**
- `int`: Exit code (0 for success, 1 for error)

**Command Line Options:**
- `url`: URL to cloak (optional, triggers interactive mode if not provided)
- `-d, --domain`: Domain to disguise as
- `-k, --keyword`: Keyword to add to the masked URL
- `-f, --format`: Output format (console, json, csv, yaml)
- `-o, --output`: Save output to file
- `--batch`: Process URLs from a file
- `--no-banner`: Disable banner display
- `--no-color`: Disable colored output
- `--services`: Specify which shortening services to use
- `--timeout`: Request timeout in seconds
- `--config`: Path to configuration file
- `--log-level`: Set logging level
- `--max-retries`: Maximum number of retries

**Example:**
```bash
# Command line usage
shadowlink https://example.com -d facebook.com -k login -f json

# Batch processing
shadowlink --batch urls.txt -d facebook.com -k login -o results.json

# Interactive mode
shadowlink
```

### CLI Functions

#### `setup_logging(config: ShadowLinkConfig) -> None`

Configure logging based on configuration settings.

#### `create_parser() -> argparse.ArgumentParser`

Create and configure the argument parser.

#### `process_single_url(url: str, domain: str, keyword: str, config: ShadowLinkConfig) -> Dict[str, Any]`

Process a single URL and return results.

#### `process_batch_file(batch_file: Path, domain: str, keyword: str, config: ShadowLinkConfig) -> List[Dict[str, Any]]`

Process URLs from a batch file.

#### `interactive_mode(config: ShadowLinkConfig) -> Optional[Dict[str, Any]]`

Run in interactive mode to get user input.

## Output Formatting

### `OutputFormatter`

Handles formatting and output of ShadowLink results.

**Methods:**

#### `__init__(config: ShadowLinkConfig)`

Initialize the output formatter.

#### `format_console(results: List[Dict[str, Any]]) -> str`

Format results for console display with colors and formatting.

#### `format_json(results: List[Dict[str, Any]]) -> str`

Format results as JSON with metadata.

#### `format_csv(results: List[Dict[str, Any]]) -> str`

Format results as CSV with headers.

#### `format_yaml(results: List[Dict[str, Any]]) -> str`

Format results as YAML (requires PyYAML).

#### `output_results(results: List[Dict[str, Any]]) -> None`

Output results in the configured format to console or file.

**Example:**
```python
from shadowlink import OutputFormatter, ShadowLinkConfig

config = ShadowLinkConfig(output_format="json")
formatter = OutputFormatter(config)

results = [
    {
        "original_url": "https://example.com",
        "domain": "facebook.com",
        "keyword": "login",
        "masked_urls": ["https://facebook.com-login@tinyurl.com/abc123"],
        "success": True,
        "errors": []
    }
]

formatter.output_results(results)
```

## Examples

### Basic Usage

```python
from shadowlink import generate_masked_urls, ValidationError, NetworkError

def cloak_url(url, domain, keyword):
    """Simple URL cloaking function."""
    try:
        masked_urls = generate_masked_urls(url, domain, keyword)
        return masked_urls
    except ValidationError as e:
        print(f"Validation error: {e.message}")
        return []
    except NetworkError as e:
        print(f"Network error: {e.message}")
        return []

# Usage
urls = cloak_url("https://example.com", "facebook.com", "login")
for url in urls:
    print(url)
```

### Advanced Configuration

```python
from shadowlink import ShadowLinkConfig, OutputFormatter
from pathlib import Path

# Create custom configuration
config = ShadowLinkConfig(
    max_retries=5,
    request_timeout=30,
    output_format="json",
    enabled_services=["tinyurl", "dagd"],
    log_level="DEBUG"
)

# Save configuration
config_path = config.get_config_dir() / "config.json"
config.save_to_file(config_path)

# Use configuration with formatter
formatter = OutputFormatter(config)
```

### Batch Processing

```python
from shadowlink import generate_masked_urls
from pathlib import Path

def process_url_file(file_path, domain, keyword):
    """Process URLs from a file."""
    results = []
    
    with open(file_path, 'r') as f:
        urls = [line.strip() for line in f if line.strip()]
    
    for url in urls:
        try:
            masked_urls = generate_masked_urls(url, domain, keyword)
            results.append({
                'original_url': url,
                'masked_urls': masked_urls,
                'success': True
            })
        except Exception as e:
            results.append({
                'original_url': url,
                'masked_urls': [],
                'success': False,
                'error': str(e)
            })
    
    return results

# Usage
results = process_url_file("urls.txt", "facebook.com", "login")
for result in results:
    if result['success']:
        print(f"✓ {result['original_url']}")
        for masked in result['masked_urls']:
            print(f"  → {masked}")
    else:
        print(f"✗ {result['original_url']}: {result['error']}")
```

### Error Handling

```python
from shadowlink import generate_masked_urls
from shadowlink.exceptions import (
    ValidationError, NetworkError, MaskingError, ShadowLinkError
)

def safe_url_cloaking(url, domain, keyword):
    """URL cloaking with comprehensive error handling."""
    try:
        masked_urls = generate_masked_urls(url, domain, keyword)
        return {
            'success': True,
            'urls': masked_urls,
            'error': None
        }
    
    except ValidationError as e:
        return {
            'success': False,
            'urls': [],
            'error': f"Validation failed: {e.message}",
            'field': e.field,
            'value': e.value
        }
    
    except NetworkError as e:
        return {
            'success': False,
            'urls': [],
            'error': f"Network error: {e.message}",
            'service': getattr(e, 'service', 'unknown')
        }
    
    except MaskingError as e:
        return {
            'success': False,
            'urls': [],
            'error': f"Masking failed: {e.message}",
            'domain': e.domain,
            'keyword': e.keyword
        }
    
    except ShadowLinkError as e:
        return {
            'success': False,
            'urls': [],
            'error': f"ShadowLink error: {e}"
        }
    
    except Exception as e:
        return {
            'success': False,
            'urls': [],
            'error': f"Unexpected error: {e}"
        }

# Usage
result = safe_url_cloaking("https://example.com", "facebook.com", "login")
if result['success']:
    print("Success!")
    for url in result['urls']:
        print(f"  {url}")
else:
    print(f"Failed: {result['error']}")
```

### Environment Configuration

```bash
# Set environment variables
export SHADOWLINK_MAX_RETRIES=5
export SHADOWLINK_OUTPUT_FORMAT=json
export SHADOWLINK_LOG_LEVEL=DEBUG
export SHADOWLINK_COLORED_OUTPUT=true
export SHADOWLINK_REQUEST_TIMEOUT=30
```

```python
from shadowlink import load_config

# Configuration will automatically load from environment
config = load_config()
print(f"Max retries: {config.max_retries}")  # Will be 5
print(f"Output format: {config.output_format}")  # Will be json
```

## Type Hints

ShadowLink is fully typed. Here are the main type definitions:

```python
from typing import List, Dict, Any, Optional, Match
from pathlib import Path

# Common types used throughout the API
URLList = List[str]
ResultDict = Dict[str, Any]
ConfigDict = Dict[str, Any]
ValidationResult = Optional[Match[str]]
```

For more detailed type information, refer to the source code or use your IDE's type checking capabilities.
