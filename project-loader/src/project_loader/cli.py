#!/usr/bin/env python3
"""
src/project_loader/cli.py

CLI entry point for project-loader. Loads and lists project details
from a configuration file (JSON or YAML).

Usage:
    project-loader <config_file>                  List all projects
    project-loader <config_file> <project_name>   Show details for a project
"""

import argparse
import json
import os
import sys
from typing import Any, Dict, List


def load_config(config_path: str) -> Dict[str, Any]:
    """
    Load project configuration from a file.

    Supports JSON and YAML formats. YAML requires the `pyyaml` package.

    Args:
        config_path: Path to the configuration file.

    Returns:
        A dictionary with project data.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the file format is not supported or parsing fails.
    """
    if not os.path.isfile(config_path):
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    _, ext = os.path.splitext(config_path)
    ext = ext.lower()

    if ext == ".json":
        try:
            with open(config_path, "r", encoding="utf-8") as fh:
                return json.load(fh)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in {config_path}: {e}")

    elif ext in (".yaml", ".yml"):
        try:
            import yaml  # type: ignore
        except ImportError:
            raise ValueError(
                "YAML support requires PyYAML. Install it with: pip install pyyaml"
            )
        try:
            with open(config_path, "r", encoding="utf-8") as fh:
                return yaml.safe_load(fh)
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in {config_path}: {e}")

    else:
        raise ValueError(
            f"Unsupported file extension '{ext}'. Use .json, .yaml, or .yml."
        )


def get_projects(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Extract the list of projects from the configuration data.

    The configuration file is expected to have a top-level key "projects"
    containing an array of project objects. Each project object should have
    at least a "name" field, and ideally a "description" field.

    Args:
        data: Parsed configuration dictionary.

    Returns:
        List of project dictionaries.

    Raises:
        ValueError: If the data structure is invalid.
    """
    projects = data.get("projects")
    if projects is None:
        # Fallback: if the data itself is a list, treat as project list
        if isinstance(data, list):
            return data
        raise ValueError(
            "Configuration must contain a 'projects' key with a list of projects."
        )
    if not isinstance(projects, list):
        raise ValueError("The 'projects' key must contain a list.")
    return projects


def list_projects(projects: List[Dict[str, Any]]) -> None:
    """
    Print a formatted list of all projects.

    Args:
        projects: List of project dictionaries.
    """
    if not projects:
        print("No projects found.")
        return

    # Determine column widths
    name_col_width = max(len(p.get("name", "")) for p in projects) + 2
    name_col_width = max(name_col_width, len("Project Name") + 2)

    desc_col_width = 60  # truncate description

    print(f"{'Project Name':<{name_col_width}} {'Description'}")
    print("-" * (name_col_width + desc_col_width))
    for proj in projects:
        name = proj.get("name", "Unnamed")
        description = proj.get("description", "")
        # Truncate long descriptions
        if len(description) > desc_col_width:
            description = description[: desc_col_width - 3] + "..."
        print(f"{name:<{name_col_width}} {description}")


def show_project(projects: List[Dict[str, Any]], project_name: str) -> None:
    """
    Print full details for a given project.

    Args:
        projects: List of project dictionaries.
        project_name: Name of the project to display.

    Raises:
        ValueError: If the project is not found.
    """
    for proj in projects:
        if proj.get("name") == project_name:
            print(f"Project: {project_name}")
            print("=" * 60)
            for key, value in proj.items():
                if key == "name":
                    continue  # already printed
                print(f"{key.capitalize()}: {value}")
            return

    raise ValueError(f"Project '{project_name}' not found.")


def parse_args(argv: List[str]) -> argparse.Namespace:
    """
    Parse command-line arguments.

    Args:
        argv: List of command line arguments (excluding program name).

    Returns:
        Parsed arguments.
    """
    parser = argparse.ArgumentParser(
        description="Load and list project details from a configuration file.",
        epilog="For more information, visit https://example.com/project-loader",
    )
    parser.add_argument(
        "config_file",
        type=str,
        help="Path to the project configuration file (JSON or YAML).",
    )
    parser.add_argument(
        "project_name",
        nargs="?",
        default=None,
        type=str,
        help="Optional project name to show detailed information.",
    )
    return parser.parse_args(argv)


def main(argv: List[str] = None) -> int:
    """
    Main entry point for the CLI.

    Args:
        argv: Command line arguments (default: sys.argv[1:]).

    Returns:
        Exit code: 0 on success, 1 on error.
    """
    if argv is None:
        argv = sys.argv[1:]

    try:
        args = parse_args(argv)
        config_data = load_config(args.config_file)
        projects = get_projects(config_data)

        if args.project_name:
            show_project(projects, args.project_name)
        else:
            list_projects(projects)

        return 0

    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
    except ValueError as e:
        print(f"Configuration error: {e}", file=sys.stderr)
    except json.JSONDecodeError as e:
        print(f"JSON parse error: {e}", file=sys.stderr)
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.", file=sys.stderr)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)

    return 1


def cli_entry():
    """Entry point for the console script (setuptools)."""
    sys.exit(main())


if __name__ == "__main__":
    sys.exit(main())