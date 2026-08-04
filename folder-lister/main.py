#!/usr/bin/env python3
"""
main.py - Entry point for folder-lister CLI.
List directories (folders) of a given path with optional recursion,
hidden folder filtering, depth control, and JSON output.
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Generator, List, Optional


def list_folders(
    base_path: Path,
    recursive: bool = True,
    exclude_hidden: bool = True,
    max_depth: Optional[int] = None,
) -> Generator[Path, None, None]:
    """
    Yield directories under `base_path` matching the given options.

    Args:
        base_path: Root directory to search.
        recursive: If True, traverse subdirectories recursively.
        exclude_hidden: If True, skip directories whose names start with '.'.
        max_depth: Maximum directory depth to traverse (None = unlimited).

    Yields:
        Path objects for each discovered directory.

    Raises:
        FileNotFoundError: If base_path does not exist.
        NotADirectoryError: If base_path is not a directory.
        PermissionError: If access is denied to base_path or a subdirectory.
    """
    if not base_path.exists():
        raise FileNotFoundError(f"Path does not exist: {base_path}")
    if not base_path.is_dir():
        raise NotADirectoryError(f"Path is not a directory: {base_path}")

    # Use os.scandir for efficient directory iteration
    def _walk(
        current_path: Path,
        current_depth: int = 0,
    ) -> Generator[Path, None, None]:
        # Depth check
        if max_depth is not None and current_depth > max_depth:
            return

        try:
            with os.scandir(current_path) as entries:
                for entry in entries:
                    if not entry.is_dir(follow_symlinks=False):
                        continue
                    dir_path = Path(entry.path)
                    # Hidden folder check
                    if exclude_hidden and entry.name.startswith("."):
                        continue
                    yield dir_path
                    if recursive:
                        yield from _walk(dir_path, current_depth + 1)
        except PermissionError:
            # Silently skip directories without permission, but log if verbose?
            # For production, we re-raise to let caller decide.
            # Here we re-raise since the caller should handle.
            raise

    yield from _walk(base_path)


def serialize_path(path: Path) -> str:
    """Convert a Path to a string (absolute or relative) for output."""
    return str(path)


def main() -> None:
    """Parse command-line arguments and display folder listing."""
    parser = argparse.ArgumentParser(
        description="List directories (folders) under a given path."
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        type=str,
        help="Root path to list folders from (default: current directory).",
    )
    parser.add_argument(
        "--recursive",
        "-r",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Recursively list subdirectories (default: enabled).",
    )
    parser.add_argument(
        "--no-recursive",
        action="store_true",
        dest="no_recursive",
        help="Disable recursive listing (alternative: --no-recursive).",
    )
    parser.add_argument(
        "--exclude-hidden",
        action=argparse.BooleanOptionalAction,
        default=True,
        dest="exclude_hidden",
        help="Exclude hidden directories (starting with '.') (default: enabled).",
    )
    parser.add_argument(
        "--show-hidden",
        action="store_true",
        dest="show_hidden",
        help="Include hidden directories (sets --no-exclude-hidden).",
    )
    parser.add_argument(
        "--max-depth",
        type=int,
        default=None,
        metavar="N",
        help="Maximum directory depth to traverse (default: unlimited).",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as a JSON array of paths.",
    )
    parser.add_argument(
        "--absolute",
        action="store_true",
        help="Print absolute paths instead of relative.",
    )

    args = parser.parse_args()

    # Resolve conflicting flags for hidden
    if args.show_hidden:
        args.exclude_hidden = False

    # Resolve --no-recursive
    if getattr(args, "no_recursive", False):
        args.recursive = False

    # Validate max_depth
    if args.max_depth is not None and args.max_depth < 0:
        parser.error("--max-depth must be a non-negative integer.")

    # Convert path to Path object
    base_path = Path(args.path).resolve()

    # Validate path existence and type
    if not base_path.exists():
        print(f"Error: Path does not exist: {base_path}", file=sys.stderr)
        sys.exit(1)
    if not base_path.is_dir():
        print(f"Error: Path is not a directory: {base_path}", file=sys.stderr)
        sys.exit(1)

    # Collect folders
    folders: List[Path] = []
    try:
        folders_gen = list_folders(
            base_path,
            recursive=args.recursive,
            exclude_hidden=args.exclude_hidden,
            max_depth=args.max_depth,
        )
        folders = list(folders_gen)
    except PermissionError as e:
        print(f"Permission denied: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)

    # Convert paths to strings
    if args.absolute:
        paths_str = [serialize_path(p.resolve()) for p in folders]
    else:
        paths_str = [serialize_path(p) for p in folders]

    # Sort for consistent output
    paths_str.sort()

    # Output
    if args.json:
        print(json.dumps(paths_str, indent=2))
    else:
        for p in paths_str:
            print(p)


if __name__ == "__main__":
    main()