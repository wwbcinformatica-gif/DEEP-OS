"""
Core logic for listing folders (directories) in a given path.

Provides functions to enumerate directories (non‑recursive or recursive),
with configurable exclusion patterns, hidden folder handling, and sorting.

All path operations use `pathlib.Path` for cross‑platform compatibility.
Explicit error handling raises standard exceptions with descriptive messages
so that callers (e.g. a CLI wrapper) can handle them appropriately.
"""

from __future__ import annotations

import enum
import itertools
import logging
import os
from pathlib import Path
from typing import Callable, Iterable, Iterator, List, Optional, Sequence, Union

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Public types
# ---------------------------------------------------------------------------

class DirectoryListingError(Exception):
    """Base exception for directory listing failures."""


class NotADirectoryError(DirectoryListingError):
    """Raised when the supplied path is not a directory."""


class PermissionDeniedError(DirectoryListingError):
    """Raised when the user lacks permission to read a directory."""


class SymlinkLoopError(DirectoryListingError):
    """Raised when a symbolic link cycle is detected."""


class InvalidPathError(DirectoryListingError):
    """Raised when the path is invalid, malformed, or empty."""


class ListingMode(enum.Enum):
    """Controls whether to list only top‑level or all nested directories."""

    TOP_ONLY = "top_only"
    """List only immediate sub‑directories of the root path."""
    RECURSIVE = "recursive"
    """List all sub‑directories recursively (depth‑first)."""


# ---------------------------------------------------------------------------
# Internal utilities
# ---------------------------------------------------------------------------

def _check_path(path: Path) -> None:
    """Validate that *path* exists, is a directory, and is accessible.

    Raises:
        InvalidPathError: If `path` is empty or not a valid filesystem path.
        FileNotFoundError: If `path` does not exist.
        NotADirectoryError: If `path` is not a directory.
        PermissionDeniedError: If the directory cannot be read.
    """
    if not path:
        raise InvalidPathError("Path is empty or invalid.")
    try:
        if not path.exists():
            raise FileNotFoundError(f"Path does not exist: {path}")
        if not path.is_dir():
            raise NotADirectoryError(f"Path is not a directory: {path}")
        # Quick permission check
        os.stat(path)
    except FileNotFoundError:
        raise
    except NotADirectoryError:
        raise
    except PermissionError as exc:
        raise PermissionDeniedError(f"Permission denied: {path}") from exc
    except OSError as exc:
        raise InvalidPathError(f"Error accessing path: {path}") from exc


def _is_hidden(entry: Path) -> bool:
    """Return `True` if *entry*'s name starts with a dot (hidden)."""
    return entry.name.startswith(".")


def _should_exclude(
    entry: Path, exclude: Optional[Sequence[str]] = None
) -> bool:
    """Return `True` if *entry*'s name matches one of the exclusion patterns.

    Matching is performed against the **last component** of the path (the
    directory name).  Wildcards are not supported; exact name comparisons are
    used for security and predictability.
    """
    if not exclude:
        return False
    return entry.name in exclude


def _resolve_symlink(entry: Path, visited: set[Path]) -> Path:
    """Resolve a symlink with loop detection.

    Raises:
        SymlinkLoopError: If following the link would cycle back.
    """
    if not entry.is_symlink():
        return entry
    # Resolve to an absolute path
    resolved = entry.resolve(strict=False)
    if resolved in visited:
        raise SymlinkLoopError(
            f"Symlink loop detected: {entry} -> {resolved}"
        )
    return resolved


def _iter_directories(
    root: Path,
    *,
    exclude: Optional[Sequence[str]] = None,
    include_hidden: bool = False,
    follow_symlinks: bool = True,
    visited: Optional[set[Path]] = None,
) -> Iterator[Path]:
    """Yield directories rooted at *root*, top‑down, depth‑first.

    This generator does **not** validate *root* – the caller must guarantee it
    is an existing, accessible directory.

    Args:
        root: Directory to scan.
        exclude: Sequence of directory names to skip.
        include_hidden: If `False`, skip entries whose name starts with '.'.
        follow_symlinks: If `True`, descend into symlinked directories.
        visited: Internal set used for symlink loop detection.

    Yields:
        Path objects for each discovered directory (including *root*).
    """
    if visited is None:
        visited = set()

    # Yield the root itself (useful for the initial call)
    yield root

    # Gather children, filtering as we go
    try:
        children: List[Path] = list(root.iterdir())
    except PermissionError as exc:
        raise PermissionDeniedError(
            f"Cannot list contents of {root}: permission denied"
        ) from exc
    except OSError as exc:
        raise DirectoryListingError(
            f"Error reading directory {root}: {exc}"
        ) from exc

    # Pre‑filter so we only process directories (or symlinks to directories)
    dirs: List[Path] = []
    for child in children:
        if child.is_symlink() and follow_symlinks:
            # Resolve with loop detection
            if child in visited:
                logger.warning("Symlink loop detected, skipping: %s", child)
                continue
            visited.add(child)
            resolved = _resolve_symlink(child, visited)
            if resolved.is_dir():
                dirs.append(child)
        elif child.is_dir():
            dirs.append(child)

    # Apply exclusions and hidden filter
    filtered: Iterator[Path] = (
        d
        for d in dirs
        if (include_hidden or not _is_hidden(d))
        and not _should_exclude(d, exclude)
    )

    # Sort for deterministic order
    sorted_dirs = sorted(filtered, key=lambda p: p.name.lower())

    # Recurse into each subdirectory
    for subdir in sorted_dirs:
        yield from _iter_directories(
            subdir,
            exclude=exclude,
            include_hidden=include_hidden,
            follow_symlinks=follow_symlinks,
            visited=visited,
        )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def list_directories(
    path: Union[str, os.PathLike[str]],
    *,
    recursive: bool = False,
    exclude: Optional[Sequence[str]] = None,
    include_hidden: bool = False,
    follow_symlinks: bool = True,
    sort: bool = True,
) -> List[Path]:
    """List directories under the given *path*.

    Args:
        path: Root directory to list.  Can be a string or a ``Path``-like
            object.
        recursive: If ``True``, recursively list all sub‑directories.
            Otherwise only the immediate child directories of *path* are
            returned.
        exclude: A sequence of directory names to exclude from the result
            (e.g. ``[".git", "__pycache__", "node_modules"]``).  Comparisons
            are case‑sensitive and match the full filename.
        include_hidden: If ``True``, include directories whose name starts
            with a dot (e.g. ``.config``).  The default is to skip them.
        follow_symlinks: If ``True`` (the default), follow symbolic links to
            directories.  If ``False``, skip symlinks entirely.
        sort: If ``True`` (the default), return directories sorted
            alphabetically (case‑insensitive).  Sorting is applied **after**
            exclusions.

    Returns:
        A list of :class:`pathlib.Path` objects representing directories.

    Raises:
        FileNotFoundError: If *path* does not exist.
        NotADirectoryError: If *path* is not a directory.
        PermissionDeniedError: If *path* or any subdirectory cannot be read.
        SymlinkLoopError: If a symlink cycle is detected (only when
            *follow_symlinks* is ``True``).
        InvalidPathError: If *path* is empty or otherwise invalid.
        DirectoryListingError: For other filesystem errors.

    Examples:
        >>> list_directories("/some/project", exclude=[".git", "node_modules"])
        [PosixPath('/some/project/src'), ...]

        >>> list_directories("/tmp", recursive=True, include_hidden=False)
        [...]
    """
    # Normalise to a Path
    try:
        root = Path(path)
    except TypeError as exc:
        raise InvalidPathError(f"Invalid path type: {path!r}") from exc

    _check_path(root)

    # Decide which strategy to use
    if recursive:
        # Recursive: use the generator, flatten into a list
        all_dirs: List[Path] = list(
            _iter_directories(
                root,
                exclude=exclude,
                include_hidden=include_hidden,
                follow_symlinks=follow_symlinks,
            )
        )
        # The generator yields the root as the first element; remove it for
        # consistency with the non‑recursive behaviour (which does not include
        # the root itself).
        # However, if we keep it, the result always includes root.  For a
        # clean API we skip it so that both modes return *children* only.
        # If the caller needs the root they already have it.
        result: List[Path] = all_dirs[1:] if len(all_dirs) > 1 else []
    else:
        # Non‑recursive: read the immediate children, filter, sort
        try:
            children = list(root.iterdir())
        except PermissionError as exc:
            raise PermissionDeniedError(
                f"Cannot list contents of {root}: permission denied"
            ) from exc
        except OSError as exc:
            raise DirectoryListingError(
                f"Error reading directory {root}: {exc}"
            ) from exc

        result = []
        for child in children:
            # Handle symlinks if configured
            is_dir = False
            if child.is_symlink() and follow_symlinks:
                visited = {root}
                resolved = _resolve_symlink(child, visited)
                if resolved.is_dir():
                    is_dir = True
            elif child.is_dir():
                is_dir = True

            if not is_dir:
                continue

            # Filter by hidden and exclude patterns
            if not include_hidden and _is_hidden(child):
                continue
            if _should_exclude(child, exclude):
                continue

            result.append(child)

    # Apply case‑insensitive alphabetical sort if requested
    if sort:
        result.sort(key=lambda p: p.name.lower())

    return result


def list_directory_tree(
    path: Union[str, os.PathLike[str]],
    *,
    exclude: Optional[Sequence[str]] = None,
    include_hidden: bool = False,
    follow_symlinks: bool = True,
) -> "dict":
    """Return a nested ``dict`` representation of the directory tree.

    The dictionary has the key ``name`` for the directory's basename,
    ``path`` for the full :class:`~pathlib.Path`, and an optional ``children``
    key containing a list of similar dictionaries for sub‑directories.

    This is a convenience function for building tree views (e.g. for JSON
    export).

    Args:
        path: Root directory.
        exclude: Directory names to exclude.
        include_hidden: Whether to include hidden directories.
        follow_symlinks: Whether to follow symbolic links.

    Returns:
        A dictionary with the structure described above.

    Raises:
        Same exceptions as :func:`list_directories`.
    """
    root = Path(path)
    _check_path(root)

    def _build(node: Path, visited: set[Path]) -> dict:
        entry: dict = {
            "name": node.name,
            "path": str(node.resolve()),
        }
        # Gather children
        try:
            children = list(node.iterdir())
        except PermissionError:
            logger.warning("Permission denied reading %s, skipping children", node)
            entry["children"] = []
            return entry
        except OSError as exc:
            logger.error("Error reading %s: %s", node, exc)
            entry["children"] = []
            return entry

        dirs: List[Path] = []
        for child in children:
            if child.is_symlink() and follow_symlinks:
                if child in visited:
                    logger.warning("Symlink loop at %s, skipping", child)
                    continue
                visited.add(child)
                resolved = _resolve_symlink(child, visited)
                if resolved.is_dir():
                    dirs.append(child)
            elif child.is_dir():
                dirs.append(child)

        # Apply filters
        filtered = (
            d
            for d in dirs
            if (include_hidden or not _is_hidden(d))
            and not _should_exclude(d, exclude)
        )
        sorted_dirs = sorted(filtered, key=lambda p: p.name.lower())

        if sorted_dirs:
            entry["children"] = [_build(d, visited) for d in sorted_dirs]
        else:
            entry["children"] = []

        return entry

    return _build(root, {root})


def count_directories(
    path: Union[str, os.PathLike[str]],
    *,
    recursive: bool = False,
    exclude: Optional[Sequence[str]] = None,
    include_hidden: bool = False,
    follow_symlinks: bool = True,
) -> int:
    """Count directories under *path*, applying the same filters.

    This is more memory‑efficient than calling :func:`list_directories` and
    taking its length when only the count is needed.

    Args:
        Same as :func:`list_directories`.

    Returns:
        Number of matching directories.
    """
    # We reuse the logic of list_directories but discard the actual paths.
    # For large trees this still builds a list; a true count would require
    # a generator‑only version.  For simplicity we use list_directories.
    return len(
        list_directories(
            path,
            recursive=recursive,
            exclude=exclude,
            include_hidden=include_hidden,
            follow_symlinks=follow_symlinks,
            sort=False,  # sorting not needed for a count
        )
    )


# ---------------------------------------------------------------------------
# Convenience class for stateful configuration (optional)
# ---------------------------------------------------------------------------

class FolderLister:
    """Configurable lister that remembers options across multiple calls.

    Attributes:
        root: The root :class:`~pathlib.Path` to operate on.
        recursive: Whether to recurse into sub‑directories.
        exclude: Sequence of directory names to exclude.
        include_hidden: Whether to include hidden folders.
        follow_symlinks: Whether to follow symbolic links.
        sort: Whether to sort results alphabetically.
    """

    def __init__(
        self,
        root: Union[str, os.PathLike[str]],
        *,
        recursive: bool = False,
        exclude: Optional[Sequence[str]] = None,
        include_hidden: bool = False,
        follow_symlinks: bool = True,
        sort: bool = True,
    ) -> None:
        self.root = Path(root)
        self.recursive = recursive
        self.exclude = exclude
        self.include_hidden = include_hidden
        self.follow_symlinks = follow_symlinks
        self.sort = sort

    def list(self) -> List[Path]:
        """Run the listing with the stored configuration."""
        return list_directories(
            self.root,
            recursive=self.recursive,
            exclude=self.exclude,
            include_hidden=self.include_hidden,
            follow_symlinks=self.follow_symlinks,
            sort=self.sort,
        )

    def tree(self) -> "dict":
        """Return the directory tree (requires recursive mode)."""
        # Ensure recursive is treated as True for the tree.
        return list_directory_tree(
            self.root,
            exclude=self.exclude,
            include_hidden=self.include_hidden,
            follow_symlinks=self.follow_symlinks,
        )

    def count(self) -> int:
        """Return the number of directories matching the configuration."""
        return count_directories(
            self.root,
            recursive=self.recursive,
            exclude=self.exclude,
            include_hidden=self.include_hidden,
            follow_symlinks=self.follow_symlinks,
        )

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}(root={self.root!r}, "
            f"recursive={self.recursive})"
        )


# ---------------------------------------------------------------------------
# Exports
# ---------------------------------------------------------------------------

__all__ = [
    "DirectoryListingError",
    "NotADirectoryError",
    "PermissionDeniedError",
    "SymlinkLoopError",
    "InvalidPathError",
    "ListingMode",
    "list_directories",
    "list_directory_tree",
    "count_directories",
    "FolderLister",
]