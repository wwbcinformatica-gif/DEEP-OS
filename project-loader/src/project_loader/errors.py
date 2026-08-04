"""
Custom exceptions for project loading errors.

This module defines the exception hierarchy for the project-loader CLI tool.
It provides consistent error types and messages for common failure scenarios.
"""

from typing import List, Optional


class ProjectLoaderError(Exception):
    """Base exception for all project-loader errors.

    Attributes:
        message: Human-readable error description.
        error_code: Optional numeric error code for programmatic handling.
    """

    def __init__(self, message: str, error_code: Optional[int] = None) -> None:
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)

    def __str__(self) -> str:
        if self.error_code is not None:
            return f"[Error {self.error_code}] {self.message}"
        return self.message

    def __repr__(self) -> str:
        return (f"{self.__class__.__name__}("
                f"message={self.message!r}, "
                f"error_code={self.error_code!r})")


class ConfigNotFoundError(ProjectLoaderError):
    """Raised when the configuration file cannot be found or accessed.

    Attributes:
        path: The file path that was attempted.
    """

    def __init__(self, path: str, message: Optional[str] = None) -> None:
        self.path = path
        default_msg = f"Configuration file not found: {path}"
        super().__init__(message or default_msg, error_code=100)


class ConfigParseError(ProjectLoaderError):
    """Raised when the configuration file is malformed or cannot be parsed.

    Attributes:
        path: Path to the configuration file.
        detail: Specific parsing error description.
    """

    def __init__(
        self,
        path: str,
        detail: str,
        message: Optional[str] = None,
    ) -> None:
        self.path = path
        self.detail = detail
        default_msg = f"Failed to parse configuration file {path}: {detail}"
        super().__init__(message or default_msg, error_code=101)


class ConfigValidationError(ProjectLoaderError):
    """Raised when the configuration file fails validation.

    Attributes:
        path: Path to the configuration file.
        errors: List of validation error messages.
    """

    def __init__(
        self,
        path: str,
        errors: List[str],
        message: Optional[str] = None,
    ) -> None:
        self.path = path
        self.errors = errors
        default_msg = (
            f"Configuration validation failed for {path}: "
            f"{'; '.join(errors)}"
        )
        super().__init__(message or default_msg, error_code=102)


class ProjectNotFoundError(ProjectLoaderError):
    """Raised when a requested project is not found in the configuration.

    Attributes:
        project_name: Name of the project that was not found.
        config_path: Optional path of the configuration file searched.
    """

    def __init__(
        self,
        project_name: str,
        config_path: Optional[str] = None,
        message: Optional[str] = None,
    ) -> None:
        self.project_name = project_name
        self.config_path = config_path
        if message:
            msg = message
        else:
            base = f"Project '{project_name}' not found"
            msg = (
                f"{base} in configuration file {config_path}"
                if config_path
                else base
            )
        super().__init__(msg, error_code=103)


class LoadingError(ProjectLoaderError):
    """Generic error during project loading.

    This is used for unexpected failures not covered by more specific
    exceptions.

    Attributes:
        message: Description of the error.
        error_code: Numeric error code (default 200).
    """

    def __init__(self, message: str, error_code: int = 200) -> None:
        super().__init__(message, error_code=error_code)