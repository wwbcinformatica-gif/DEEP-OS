"""project_loader - CLI tool to load and list project details from a config file."""

from __future__ import annotations

import importlib.metadata
import logging
from typing import Final, List, Optional

# ---------------------------------------------------------------------------
# Package metadata
# ---------------------------------------------------------------------------

__all__: Final[List[str]] = [
    "ProjectLoader",
    "ConfigLoader",
    "Project",
    "__version__",
    "__author__",
    "__email__",
    "__license__",
    "get_version",
    "setup_logging",
]

__author__: str = "Project Loader Team"
__email__: str = "team@projectloader.dev"
__license__: str = "MIT"

# ---------------------------------------------------------------------------
# Version handling
# ---------------------------------------------------------------------------

_PACKAGE_NAME: str = "project-loader"


def get_version() -> str:
    """Return the installed version of project-loader.

    Uses ``importlib.metadata`` to retrieve the version. If the package
    is not installed (e.g., during development), returns ``"unknown"``.

    Returns
    -------
    str
        Version string in PEP 440 format or ``"unknown"``.
    """
    try:
        return importlib.metadata.version(_PACKAGE_NAME)
    except importlib.metadata.PackageNotFoundError:
        return "unknown"
    except Exception as exc:
        logging.getLogger(__name__).warning(
            "Failed to retrieve package version: %s", exc
        )
        return "unknown"


__version__: str = get_version()

# ---------------------------------------------------------------------------
# Lazily imported core classes
# ---------------------------------------------------------------------------

_loader: Optional["ProjectLoader"] = None
_config_loader: Optional["ConfigLoader"] = None
_project_class: Optional["Project"] = None


def _lazy_import(name: str, module_path: str) -> type:
    """Import and return a class from a submodule lazily.

    Parameters
    ----------
    name : str
        The name of the object to import.
    module_path : str
        The dotted submodule path (e.g., ``.loader``).

    Returns
    -------
    type
        The imported class or function.

    Raises
    ------
    ImportError
        If the submodule or object does not exist.
    """
    import importlib

    try:
        module = importlib.import_module(module_path, package=__name__)
    except ImportError as err:
        raise ImportError(
            f"Cannot import '{name}' from '{module_path}': {err}"
        ) from err

    if not hasattr(module, name):
        raise ImportError(f"Module '{module_path}' does not have '{name}'")

    return getattr(module, name)


def ProjectLoader(*args, **kwargs) -> "ProjectLoader":
    """Get a singleton instance of :class:`ProjectLoader`.

    The first call creates and caches the instance; subsequent calls
    return the same object.  Accepts the same arguments as the class
    constructor.

    Returns
    -------
    ProjectLoader
        An instance of the project loader.
    """
    global _loader
    if _loader is None:
        cls = _lazy_import("ProjectLoader", ".loader")
        _loader = cls(*args, **kwargs)
    return _loader


def ConfigLoader(*args, **kwargs) -> "ConfigLoader":
    """Get a singleton instance of :class:`ConfigLoader`.

    The first call creates and caches the instance; subsequent calls
    return the same object.  Accepts the same arguments as the class
    constructor.

    Returns
    -------
    ConfigLoader
        An instance of the config loader.
    """
    global _config_loader
    if _config_loader is None:
        cls = _lazy_import("ConfigLoader", ".config")
        _config_loader = cls(*args, **kwargs)
    return _config_loader


def Project(*args, **kwargs) -> "Project":
    """Get a singleton instance of :class:`Project`.

    The first call creates and caches the instance; subsequent calls
    return the same object.  Accepts the same arguments as the class
    constructor.

    Returns
    -------
    Project
        An instance of the project model.
    """
    global _project_class
    if _project_class is None:
        cls = _lazy_import("Project", ".project")
        _project_class = cls(*args, **kwargs)
    return _project_class

# ---------------------------------------------------------------------------
# Logging configuration
# ---------------------------------------------------------------------------

def setup_logging(level: int = logging.INFO) -> None:
    """Configure package-level logging.

    Parameters
    ----------
    level : int, optional
        Logging level, e.g., ``logging.DEBUG`` (default: ``logging.INFO``).
    """
    logger = logging.getLogger(__name__)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    logger.setLevel(level)
    # Prevent propagation to root logger to avoid duplicate messages
    logger.propagate = False

# ---------------------------------------------------------------------------
# Top-level convenience imports (for documentation / static analysis)
# ---------------------------------------------------------------------------

# NOTE: The actual imports are resolved lazily at runtime.  These lines
# are only used for type checkers and IDE autocompletion when the
# submodules are available.  They will be silently ignored if the
# submodules don't exist yet.
try:
    from .loader import ProjectLoader as _ProjectLoader  # noqa: F401
    from .config import ConfigLoader as _ConfigLoader    # noqa: F401
    from .project import Project as _Project             # noqa: F401
except ImportError:
    pass