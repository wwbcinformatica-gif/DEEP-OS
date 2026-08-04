#!/usr/bin/env python3
"""
Entry point for the project_loader CLI tool.

Allows the package to be executed using ``python -m project_loader``.

This module provides a command-line interface that loads a JSON configuration
file containing project metadata and displays it in a human-readable format or
as JSON output.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence


def load_config(config_path: str) -> Dict[str, Any]:
    """
    Load and validate a JSON configuration file.

    Args:
        config_path: Path to the JSON configuration file.

    Returns:
        Parsed configuration dictionary.

    Raises:
        FileNotFoundError: If the configuration file does not exist.
        json.JSONDecodeError: If the file contains invalid JSON.
        ValueError: If the configuration is missing required keys.
    """
    path = Path(config_path)

    if not path.is_file():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    with path.open("r", encoding="utf-8") as f:
        config: Dict[str, Any] = json.load(f)

    # Validate required fields
    required_keys = {"project", "version"}
    missing = required_keys - config.keys()
    if missing:
        raise ValueError(
            f"Configuration is missing required key(s): {', '.join(sorted(missing))}"
        )

    return config


def format_project_details(config: Dict[str, Any], pretty: bool = False) -> str:
    """
    Format project details as a human-readable string.

    Args:
        config: The project configuration dictionary.
        pretty: If True, use a more detailed formatting style.

    Returns:
        Formatted string representation of the project details.
    """
    lines: List[str] = []
    lines.append(f"Project: {config['project']}")
    lines.append(f"Version: {config['version']}")

    if "description" in config:
        lines.append(f"Description: {config['description']}")

    if "authors" in config:
        authors = config["authors"]
        if isinstance(authors, list):
            author_str = ", ".join(str(a) for a in authors)
        else:
            author_str = str(authors)
        lines.append(f"Authors: {author_str}")

    if "license" in config:
        lines.append(f"License: {config['license']}")

    if "repository" in config:
        lines.append(f"Repository: {config['repository']}")

    if "homepage" in config:
        lines.append(f"Homepage: {config['homepage']}")

    if "dependencies" in config:
        deps = config["dependencies"]
        if isinstance(deps, dict):
            lines.append("Dependencies:")
            for dep, ver in deps.items():
                lines.append(f"  - {dep}: {ver}")
        elif isinstance(deps, list):
            lines.append("Dependencies:")
            for dep in deps:
                lines.append(f"  - {dep}")

    # Add any extra keys not explicitly handled
    known_keys = {
        "project", "version", "description", "authors", "license",
        "repository", "homepage", "dependencies"
    }
    extra = {k: v for k, v in config.items() if k not in known_keys}
    if extra:
        lines.append("Additional Details:")
        for key, value in extra.items():
            lines.append(f"  {key}: {value}")

    return "\n".join(lines)


def display_json_output(config: Dict[str, Any], indent: Optional[int] = None) -> None:
    """
    Output the configuration as formatted JSON.

    Args:
        config: The project configuration dictionary.
        indent: Number of spaces for indentation (None for compact output).
    """
    json.dump(config, sys.stdout, indent=indent)
    sys.stdout.write("\n")


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    """
    Parse command-line arguments.

    Args:
        argv: Optional argument sequence (defaults to sys.argv[1:]).

    Returns:
        Parsed arguments namespace.
    """
    parser = argparse.ArgumentParser(
        description="Load and list project details from a configuration file.",
        prog="python -m project_loader",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Example:\n"
            "  python -m project_loader project.json\n"
            "  python -m project_loader project.json --json\n"
            "  python -m project_loader project.json --pretty\n"
        ),
    )
    parser.add_argument(
        "config",
        type=str,
        help="Path to the JSON configuration file.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output the configuration as JSON (default: human-readable).",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Enable more detailed formatting in human-readable output.",
    )
    parser.add_argument(
        "--indent",
        type=int,
        default=2,
        help="Number of spaces for JSON indentation (default: 2, use 0 for compact).",
    )
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> int:
    """
    Main entry point for the CLI tool.

    Args:
        argv: Optional argument sequence (defaults to sys.argv[1:]).

    Returns:
        Exit code (0 for success, 1 for error).
    """
    try:
        args = parse_args(argv)
        config = load_config(args.config)

        if args.json:
            indent = args.indent if args.indent > 0 else None
            display_json_output(config, indent=indent)
        else:
            output = format_project_details(config, pretty=args.pretty)
            print(output)

        return 0

    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except json.JSONDecodeError as e:
        print(
            f"Error: Invalid JSON in configuration file: {e}",
            file=sys.stderr,
        )
        return 1
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())