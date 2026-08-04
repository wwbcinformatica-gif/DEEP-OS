"""
Test package for project-loader.

This package contains unit tests for the project-loader CLI tool.
It validates that the tool loads and lists project details from a
configuration file correctly.

Automatically configures the module search path so that the main
source package can be imported during testing, and verifies the
presence of required test dependencies.
"""

import sys
import os

# ------------------------------------------------------------------------
# Environment setup
# ------------------------------------------------------------------------
def _setup_test_path() -> None:
    """
    Add the project root directory to ``sys.path`` so that the
    ``project_loader`` package is importable during tests.

    The project root is assumed to be the parent directory of this
    test package (i.e., one level up from ``tests/__init__.py``).
    The path is inserted at the beginning of the module search list
    to override any previously installed versions.
    """
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

# ------------------------------------------------------------------------
# Dependency validation
# ------------------------------------------------------------------------
def _validate_dependencies() -> None:
    """
    Ensure that all required libraries for running the test suite
    are available.

    Raises
    ------
    RuntimeError
        If a mandatory dependency is missing or Python version is
        too old.
    """
    # Python version check
    if sys.version_info < (3, 6):
        raise RuntimeError(
            "project-loader requires at least Python 3.6. "
            f"Current version: {sys.version_info.major}.{sys.version_info.minor}."
        )

    # Required testing framework
    try:
        import pytest  # noqa: F401 – we only check availability
    except ImportError:
        raise RuntimeError(
            "The pytest library is required to run the tests. "
            "Install it with: pip install pytest"
        )

    # Verify the main package can be imported (this also ensures
    # all its dependencies are satisfied)
    try:
        import project_loader  # noqa: F401
    except ImportError as e:
        raise RuntimeError(
            "Cannot import the 'project_loader' package. "
            "Please ensure it is installed or that the source "
            "directory is present and correctly structured."
        ) from e

# ------------------------------------------------------------------------
# Package initialisation
# ------------------------------------------------------------------------
try:
    _setup_test_path()
    _validate_dependencies()
except Exception as exc:
    # Re-raise with a clear message intended for test discovery
    raise RuntimeError(
        f"Failed to initialise the test package: {exc}"
    ) from exc

# Clean up helper names (they are not needed after initialisation)
del _setup_test_path, _validate_dependencies