import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, List, Optional, Union


class ProjectLoadError(Exception):
    """Base exception for project loading errors."""


class ProjectValidationError(ProjectLoadError):
    """Exception raised when the project configuration is invalid."""


@dataclass
class Project:
    """Represents a project loaded from a configuration file."""

    name: str
    version: Optional[str] = None
    description: Optional[str] = None
    url: Optional[str] = None
    author: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Validate project fields after initialization."""
        if not self.name or not self.name.strip():
            raise ProjectValidationError("Project name cannot be empty")
        if self.version is not None and not isinstance(self.version, str):
            raise ProjectValidationError("Version must be a string")
        if self.description is not None and not isinstance(self.description, str):
            raise ProjectValidationError("Description must be a string")
        if self.url is not None and not isinstance(self.url, str):
            raise ProjectValidationError("URL must be a string")
        if self.author is not None and not isinstance(self.author, str):
            raise ProjectValidationError("Author must be a string")
        if not isinstance(self.dependencies, list):
            raise ProjectValidationError("Dependencies must be a list")
        for dep in self.dependencies:
            if not isinstance(dep, str):
                raise ProjectValidationError(
                    f"Each dependency must be a string, got {type(dep).__name__}"
                )


def _get_required_field(data: dict, key: str, target_type: type = str) -> Any:
    """Get a required field from data dict, ensuring it exists and is of the correct type.

    Args:
        data: The dictionary to extract the field from.
        key: The field name.
        target_type: Expected type of the field value.

    Returns:
        The field value.

    Raises:
        ProjectValidationError: If the field is missing or has wrong type.
    """
    if key not in data:
        raise ProjectValidationError(f"Missing required field: '{key}'")
    value = data[key]
    if not isinstance(value, target_type):
        raise ProjectValidationError(
            f"Field '{key}' must be of type {target_type.__name__}, "
            f"got {type(value).__name__}"
        )
    return value


def _get_optional_field(data: dict, key: str, target_type: type = str) -> Optional[Any]:
    """Get an optional field from data dict, returning None if not present.

    If the field exists, its type is validated.

    Args:
        data: The dictionary to extract the field from.
        key: The field name.
        target_type: Expected type of the field value.

    Returns:
        The field value or None.

    Raises:
        ProjectValidationError: If the field has a value but it is of the wrong type.
    """
    if key not in data or data[key] is None:
        return None
    value = data[key]
    if not isinstance(value, target_type):
        raise ProjectValidationError(
            f"Field '{key}' must be of type {target_type.__name__}, "
            f"got {type(value).__name__}"
        )
    return value


def load_project(filepath: Union[str, Path]) -> Project:
    """Load a project from a JSON file and return a Project object.

    Args:
        filepath: Path to the JSON configuration file.

    Returns:
        A Project instance populated with data from the file.

    Raises:
        FileNotFoundError: If the specified file does not exist.
        ProjectValidationError: If the JSON data is invalid or missing required fields.
        json.JSONDecodeError: If the file contains invalid JSON.
    """
    path = Path(filepath) if isinstance(filepath, str) else filepath

    if not path.exists():
        raise FileNotFoundError(f"Project file not found: {path}")
    if not path.is_file():
        raise ProjectValidationError(f"Path is not a file: {path}")

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        raise ProjectValidationError(f"Invalid JSON in project file: {e}") from e

    if not isinstance(data, dict):
        raise ProjectValidationError(
            "Project file must contain a JSON object (dictionary)"
        )

    # Extract required and optional fields
    name = _get_required_field(data, "name", str)
    version = _get_optional_field(data, "version", str)
    description = _get_optional_field(data, "description", str)
    url = _get_optional_field(data, "url", str)
    author = _get_optional_field(data, "author", str)

    # Handle dependencies: optional list of strings
    dependencies_raw = _get_optional_field(data, "dependencies", list)
    dependencies: List[str] = []
    if dependencies_raw is not None:
        for dep in dependencies_raw:
            if not isinstance(dep, str):
                raise ProjectValidationError(
                    f"Each dependency must be a string, got {type(dep).__name__}"
                )
            dependencies.append(dep)

    # Create and return validated Project instance
    return Project(
        name=name,
        version=version,
        description=description,
        url=url,
        author=author,
        dependencies=dependencies,
    )