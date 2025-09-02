"""Output formatting and file handling for ShadowLink results.

This module provides different output formats including console display,
JSON, CSV, and YAML formats for integration with other tools.
"""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path
from typing import List, Dict, Any, TextIO
import logging

from .config import ShadowLinkConfig

logger = logging.getLogger(__name__)

# Terminal colors (only used when colored output is enabled)
RED = "\033[31m"
GRN = "\033[32m"
YLW = "\033[33m"
CYN = "\033[36m"
RST = "\033[0m"

try:
    import yaml

    YAML_AVAILABLE = True
except ImportError:
    yaml = None
    YAML_AVAILABLE = False


class OutputFormatter:
    """Handles formatting and output of ShadowLink results."""

    def __init__(self, config: ShadowLinkConfig):
        """Initialize the output formatter.

        Args:
            config: Configuration object with output settings
        """
        self.config = config
        self.colors_enabled = config.colored_output and sys.stdout.isatty()

    def _colorize(self, text: str, color: str) -> str:
        """Apply color to text if colors are enabled.

        Args:
            text: Text to colorize
            color: ANSI color code

        Returns:
            Colorized text or plain text if colors disabled
        """
        if self.colors_enabled:
            return f"{color}{text}{RST}"
        return text

    def format_console(self, results: List[Dict[str, Any]]) -> str:
        """Format results for console display.

        Args:
            results: List of processing results

        Returns:
            Formatted string for console output
        """
        output_lines = []

        for i, result in enumerate(results, 1):
            if len(results) > 1:
                output_lines.append(f"\n{self._colorize(f'=== Result {i} ===', CYN)}")

            output_lines.append(f"{self._colorize('Original URL:', CYN)} {result['original_url']}")
            output_lines.append(f"{self._colorize('Domain:', CYN)} {result['domain']}")
            output_lines.append(f"{self._colorize('Keyword:', CYN)} {result['keyword']}")

            if result["success"]:
                output_lines.append(
                    f"\n{self._colorize('[✓] Successfully generated masked URLs:', GRN)}"
                )
                for j, masked_url in enumerate(result["masked_urls"], 1):
                    output_lines.append(f"{self._colorize(f'➤ Link {j}:', CYN)} {masked_url}")
            else:
                output_lines.append(f"\n{self._colorize('[✖] Failed to generate URLs:', RED)}")
                for error in result["errors"]:
                    output_lines.append(f"{self._colorize('Error:', RED)} {error}")

        return "\n".join(output_lines)

    def format_json(self, results: List[Dict[str, Any]]) -> str:
        """Format results as JSON.

        Args:
            results: List of processing results

        Returns:
            JSON formatted string
        """
        output_data = {
            "shadowlink_version": "0.0.1",
            "total_processed": len(results),
            "successful": sum(1 for r in results if r["success"]),
            "failed": sum(1 for r in results if not r["success"]),
            "results": results,
        }

        return json.dumps(output_data, indent=2, ensure_ascii=False)

    def format_csv(self, results: List[Dict[str, Any]]) -> str:
        """Format results as CSV.

        Args:
            results: List of processing results

        Returns:
            CSV formatted string
        """
        import io

        output = io.StringIO()
        writer = csv.writer(output)

        # Write header
        writer.writerow(
            [
                "original_url",
                "domain",
                "keyword",
                "success",
                "masked_url_1",
                "masked_url_2",
                "masked_url_3",
                "masked_url_4",
                "errors",
            ]
        )

        # Write data rows
        for result in results:
            masked_urls = result["masked_urls"] + [""] * (4 - len(result["masked_urls"]))
            errors = "; ".join(result["errors"]) if result["errors"] else ""

            writer.writerow(
                [
                    result["original_url"],
                    result["domain"],
                    result["keyword"],
                    result["success"],
                    *masked_urls[:4],
                    errors,
                ]
            )

        return output.getvalue()

    def format_yaml(self, results: List[Dict[str, Any]]) -> str:
        """Format results as YAML.

        Args:
            results: List of processing results

        Returns:
            YAML formatted string
        """
        if YAML_AVAILABLE and yaml is not None:
            output_data = {
                "shadowlink_version": "0.0.1",
                "total_processed": len(results),
                "successful": sum(1 for r in results if r["success"]),
                "failed": sum(1 for r in results if not r["success"]),
                "results": results,
            }

            return yaml.dump(output_data, default_flow_style=False, allow_unicode=True)
        else:
            logger.warning("PyYAML not installed, falling back to JSON format")
            return self.format_json(results)

    def output_results(self, results: List[Dict[str, Any]]) -> None:
        """Output results in the configured format.

        Args:
            results: List of processing results
        """
        # Choose formatter based on configuration
        formatters = {
            "console": self.format_console,
            "json": self.format_json,
            "csv": self.format_csv,
            "yaml": self.format_yaml,
        }

        formatter = formatters.get(self.config.output_format, self.format_console)
        formatted_output = formatter(results)

        # Output to file or console
        if self.config.save_to_file and self.config.output_file:
            try:
                output_path = Path(self.config.output_file)
                output_path.parent.mkdir(parents=True, exist_ok=True)

                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(formatted_output)

                logger.info(f"Results saved to {output_path}")

                # Also show summary on console
                if self.config.output_format != "console":
                    summary = self._create_summary(results)
                    print(summary)

            except Exception as e:
                logger.error(f"Failed to save output to file: {e}")
                print(f"✖ Failed to save output: {e}")
                print("\nResults:")
                print(formatted_output)
        else:
            print(formatted_output)

    def _create_summary(self, results: List[Dict[str, Any]]) -> str:
        """Create a summary of processing results.

        Args:
            results: List of processing results

        Returns:
            Summary string
        """
        total = len(results)
        successful = sum(1 for r in results if r["success"])
        failed = total - successful

        summary_lines = [
            f"\n{self._colorize('=== Processing Summary ===', CYN)}",
            f"Total URLs processed: {total}",
            f"{self._colorize('Successful:', GRN)} {successful}",
            f"{self._colorize('Failed:', RED)} {failed}",
        ]

        if self.config.output_file:
            summary_lines.append(f"Results saved to: {self.config.output_file}")

        return "\n".join(summary_lines)
