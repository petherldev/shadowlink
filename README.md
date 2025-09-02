# ShadowLink

ShadowLink is a **powerful, lightweight, and terminal-based URL masking tool** designed for ethical use in cybersecurity demonstrations, phishing awareness training, and red teaming exercises.

It allows you to **generate deceptive but legitimate-looking URLs** by masking original links with custom domains and keywords—perfect for simulating real-world phishing behavior in a controlled environment.

[![Python Version](https://img.shields.io/pypi/pyversions/shadowlink?style=flat-square&color=blueviolet&logo=python&logoColor=white)](https://python.org)
[![Version](https://img.shields.io/pypi/v/shadowlink?style=flat-square&color=green&logo=pypi&logoColor=white)](https://pypi.org/project/shadowlink)
[![License](https://img.shields.io/github/license/petherldev/shadowlink?style=flat-square&color=blue&logo=github&logoColor=white)](https://opensource.org/licenses/MIT)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![PyPI Downloads](https://static.pepy.tech/personalized-badge/shadowlink?period=total&units=INTERNATIONAL_SYSTEM&left_color=GREY&right_color=BRIGHTGREEN&left_text=downloads)](https://pepy.tech/projects/shadowlink)

> [!CAUTION]
>
> This tool is developed **strictly for educational and ethical purposes** such as:
> - Cybersecurity training
> - Social engineering awareness
> - Red team operations
>
> Any misuse of this tool for malicious purposes is **strongly discouraged and illegal**. The author is not responsible for any misuse or damage caused.

## Features

- **Multiple URL Shortening Services**: Supports TinyURL, Da.gd, Clck.ru, and OSDB
- **Domain Masking**: Disguise URLs behind trusted domains like facebook.com, google.com
- **Batch Processing**: Process multiple URLs from files
- **Multiple Output Formats**: Console, JSON, CSV, and YAML output
- **Configuration Management**: File-based and environment variable configuration
- **Production Ready**: Comprehensive error handling, logging, and validation
- **CLI & Interactive Modes**: Use as command-line tool or interactive interface

## Installation

### From PyPI (Recommended)

```bash
pip3 install shadowlink
```

### From Source

```bash
git clone https://github.com/petherldev/shadowlink.git
cd shadowlink
pip3 install -e .
```

### Development Installation

```bash
git clone https://github.com/petherldev/shadowlink.git
cd shadowlink
pip3 install -e ".[dev]"
```

## Quick Start

### Interactive Mode

Simply run the command and follow the prompts:

```bash
shadowlink
```

### Command Line Mode

```bash
shadowlink https://example.com/long/url -d facebook.com -k login
```

### Batch Processing

```bash
shadowlink --batch urls.txt -d google.com -k verify
```

## Usage Examples

### Basic Usage

```bash
# Interactive mode
shadowlink

# Command line with all parameters
shadowlink "https://malicious-site.com/phishing" -d "facebook.com" -k "login"

# Output: https://facebook.com-login@tinyurl.com/abc123
```

### Advanced Usage

```bash
# Save results to JSON file
shadowlink https://example.com -d google.com -k verify -f json -o results.json

# Use specific services only
shadowlink https://example.com -d twitter.com -k signup --services tinyurl dagd

# Batch process with custom timeout
shadowlink --batch urls.txt -d facebook.com -k login --timeout 30

# Disable colors and banner
shadowlink https://example.com -d google.com -k test --no-color --no-banner
```

### Python API

```python
from shadowlink import mask_url, validate_url, generate_masked_urls

# Validate a URL
if validate_url("https://example.com"):
    print("Valid URL")

# Generate masked URLs
masked_urls = generate_masked_urls(
    "https://example.com", 
    "facebook.com", 
    "login"
)

for url in masked_urls:
    print(url)
```

## Configuration

### Configuration File

ShadowLink supports configuration files in JSON format. The configuration is loaded from:

1. Environment variables (highest priority)
2. User config file (`~/.config/shadowlink/config.json`)
3. System config file (`/etc/shadowlink/config.json`)
4. Default values (lowest priority)

Example configuration file:

```json
{
  "max_keyword_length": 15,
  "max_retries": 3,
  "request_timeout": 10,
  "output_format": "console",
  "colored_output": true,
  "show_banner": true,
  "enabled_services": ["tinyurl", "dagd", "clckru", "osdb"],
  "log_level": "INFO",
  "enable_cache": true,
  "cache_ttl": 3600
}
```

### Environment Variables

All configuration options can be set via environment variables with the `SHADOWLINK_` prefix:

```bash
export SHADOWLINK_MAX_RETRIES=5
export SHADOWLINK_OUTPUT_FORMAT=json
export SHADOWLINK_LOG_LEVEL=DEBUG
export SHADOWLINK_COLORED_OUTPUT=false
```

### Save Current Configuration

```bash
shadowlink --save-config
```

## Command Line Options

```
usage: shadowlink [-h] [--version] [-d DOMAIN] [-k KEYWORD] [-f {console,json,csv,yaml}]
                  [-o OUTPUT] [--no-banner] [--no-color] [--services {tinyurl,dagd,clckru,osdb} ...]
                  [--timeout TIMEOUT] [--config CONFIG] [--save-config]
                  [--log-level {DEBUG,INFO,WARNING,ERROR}] [--log-file LOG_FILE]
                  [--batch BATCH] [--max-retries MAX_RETRIES]
                  [url]

Ultimate URL Cloaking Tool - mask URLs behind trusted domains

positional arguments:
  url                   URL to cloak (if not provided, interactive mode is used)

options:
  -h, --help            show this help message and exit
  --version             show program's version number and exit
  -d DOMAIN, --domain DOMAIN
                        Domain to disguise as (e.g., facebook.com)
  -k KEYWORD, --keyword KEYWORD
                        Keyword to add to the masked URL
  -f {console,json,csv,yaml}, --format {console,json,csv,yaml}
                        Output format (default: console)
  -o OUTPUT, --output OUTPUT
                        Save output to file
  --no-banner           Disable banner display
  --no-color            Disable colored output
  --services {tinyurl,dagd,clckru,osdb} ...
                        Specify which shortening services to use
  --timeout TIMEOUT     Request timeout in seconds
  --config CONFIG       Path to configuration file
  --save-config         Save current settings to user config file
  --log-level {DEBUG,INFO,WARNING,ERROR}
                        Set logging level
  --log-file LOG_FILE   Log to file instead of console
  --batch BATCH         Process URLs from a file (one URL per line)
  --max-retries MAX_RETRIES
                        Maximum number of retries for failed requests
```

## Output Formats

### Console (Default)

```
Original URL: https://example.com
Domain: facebook.com
Keyword: login

[✓] Successfully generated masked URLs:
➤ Link 1: https://facebook.com-login@tinyurl.com/abc123
➤ Link 2: https://facebook.com-login@da.gd/xyz789
```

### JSON

```json
{
  "shadowlink_version": "0.0.1",
  "total_processed": 1,
  "successful": 1,
  "failed": 0,
  "results": [
    {
      "original_url": "https://example.com",
      "domain": "facebook.com",
      "keyword": "login",
      "masked_urls": [
        "https://facebook.com-login@tinyurl.com/abc123",
        "https://facebook.com-login@da.gd/xyz789"
      ],
      "errors": [],
      "success": true
    }
  ]
}
```

### CSV

```csv
original_url,domain,keyword,success,masked_url_1,masked_url_2,masked_url_3,masked_url_4,errors
https://example.com,facebook.com,login,True,https://facebook.com-login@tinyurl.com/abc123,https://facebook.com-login@da.gd/xyz789,,,
```

## Security Considerations

**Important**: ShadowLink is designed for legitimate security research, penetration testing, and educational purposes. Please use responsibly and in accordance with applicable laws and regulations.

### Legitimate Use Cases

- **Security Research**: Testing URL filtering and detection systems
- **Penetration Testing**: Authorized security assessments
- **Education**: Learning about URL manipulation and security
- **Privacy**: Protecting sensitive URLs from analysis

### Ethical Guidelines

- Only use on systems you own or have explicit permission to test
- Respect terms of service of URL shortening services
- Do not use for malicious purposes, phishing, or fraud
- Be transparent about your testing activities when appropriate

## Development

### Setting Up Development Environment

```bash
git clone https://github.com/petherldev/shadowlink.git
cd shadowlink
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e ".[dev]"
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=shadowlink

# Run specific test file
pytest tests/test_shadowlink.py

# Run with verbose output
pytest -v
```

### Code Quality

```bash
# Format code
black shadowlink/ tests/
```

## Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Quick Contribution Guide

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass (`pytest`)
6. Format your code (`black .`)
7. Commit your changes (`git commit -m 'Add amazing feature'`)
8. Push to the branch (`git push origin feature/amazing-feature`)
9. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [pyshorteners](https://github.com/ellisonleao/pyshorteners) - URL shortening service integration
- All URL shortening service providers
- The Python community for excellent tooling and libraries

## Support

- **Issues**: [GitHub Issues](https://github.com/petherldev/shadowlink/issues)
- **Email**: petherl@protonmail.com
