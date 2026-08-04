from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------


class ProjectValidationError(ValueError):
    """Raised when a project configuration fails validation."""
    pass


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class DependencyType(str):
    """Standard dependency categories used in project configs."""
    PRODUCTION = "production"
    DEVELOPMENT = "development"
    OPTIONAL = "optional"
    PEER = "peer"


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Author:
    """Represents a project author."""

    name: str
    email: Optional[str] = None

    def __post_init__(self) -> None:
        if not self.name or not self.name.strip():
            raise ProjectValidationError("Author name must not be empty.")
        if self.email is not None and not re.match(r"[^@]+@[^@]+\.[^@]+", self.email):
            raise ProjectValidationError(
                f"Author email '{self.email}' is not a valid email address."
            )


@dataclass(frozen=True)
class Dependency:
    """A single project dependency with optional version constraint."""

    name: str
    version: Optional[str] = None
    type: DependencyType = DependencyType.PRODUCTION

    def __post_init__(self) -> None:
        if not self.name or not self.name.strip():
            raise ProjectValidationError("Dependency name must not be empty.")
        if not isinstance(self.type, DependencyType):
            raise ProjectValidationError(
                f"Dependency type must be a DependencyType enum, got {type(self.type)}."
            )


@dataclass(frozen=True)
class Script:
    """A named script/task with an associated shell command."""

    name: str
    command: str
    description: Optional[str] = None

    def __post_init__(self) -> None:
        if not self.name or not self.name.strip():
            raise ProjectValidationError("Script name must not be empty.")
        if not self.command or not self.command.strip():
            raise ProjectValidationError(
                f"Script '{self.name}' must have a non-empty command."
            )


@dataclass(frozen=True)
class PathConfig:
    """Configurable paths for a project (source, tests, output, etc.)."""

    source: Path = field(default=Path("src"))
    tests: Path = field(default=Path("tests"))
    output: Path = field(default=Path("dist"))
    docs: Optional[Path] = None
    static: Optional[Path] = None

    def __post_init__(self) -> None:
        for field_name in ("source", "tests", "output"):
            path = getattr(self, field_name)
            if not isinstance(path, Path):
                raise ProjectValidationError(
                    f"PathConfig.{field_name} must be a pathlib.Path, "
                    f"got {type(path)}."
                )
        # Ensure relative paths are not absolute (config files should use relative paths)
        for field_name in self.__dataclass_fields__:
            path = getattr(self, field_name)
            if path is not None and path.is_absolute():
                raise ProjectValidationError(
                    f"PathConfig.{field_name} must be a relative path, "
                    f"got absolute path '{path}'."
                )


@dataclass(frozen=True)
class PythonSettings:
    """Python‑specific settings such as required version and build backend."""

    python_version: Optional[str] = None
    build_backend: Optional[str] = None
    requires_python: Optional[str] = None

    def __post_init__(self) -> None:
        # Basic semver pattern check (loose)
        if self.python_version is not None:
            if not re.match(r"^\d+\.\d+(\.\d+)?$", self.python_version):
                raise ProjectValidationError(
                    f"Python version '{self.python_version}' is not a valid "
                    f"semver string (e.g., '3.10' or '3.10.4')."
                )
        if self.requires_python is not None:
            if not re.match(r"^[><=!~]+\s*\d+\.\d+(\.\d+)?", self.requires_python):
                # Accept simple specifiers like ">=3.8" or "!=3.10.0"
                raise ProjectValidationError(
                    f"requires_python '{self.requires_python}' does not look like "
                    f"a valid PEP 440 version specifier."
                )


@dataclass(frozen=True)
class ProjectMetadata:
    """Core metadata of a project."""

    name: str
    version: str = "0.1.0"
    description: str = ""
    license: Optional[str] = None
    authors: Sequence[Author] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.name or not self.name.strip():
            raise ProjectValidationError("Project name must not be empty.")
        if not isinstance(self.authors, (list, tuple)):
            raise ProjectValidationError(
                f"Authors must be a list/tuple of Author instances, "
                f"got {type(self.authors)}."
            )


@dataclass(frozen=True)
class Project:
    """Top‑level representation of a project loaded from configuration."""

    metadata: ProjectMetadata
    dependencies: Sequence[Dependency] = field(default_factory=list)
    dev_dependencies: Sequence[Dependency] = field(default_factory=list)
    scripts: Sequence[Script] = field(default_factory=list)
    paths: PathConfig = field(default_factory=PathConfig)
    python: PythonSettings = field(default_factory=PythonSettings)
    # Additional custom settings (key‑value store)
    custom: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for field_name in ("metadata", "paths", "python"):
            value = getattr(self, field_name)
            if not isinstance(value, (ProjectMetadata, PathConfig, PythonSettings)):
                raise ProjectValidationError(
                    f"Project.{field_name} must be an instance of its respective "
                    f"dataclass, got {type(value)}."
                )
        # Ensure lists contain the correct types
        for collection_name in ("dependencies", "dev_dependencies", "scripts"):
            collection = getattr(self, collection_name)
            expected_type = Dependency if "depend" in collection_name else Script
            for item in collection:
                if not isinstance(item, expected_type):
                    raise ProjectValidationError(
                        f"Project.{collection_name} must only contain "
                        f"{expected_type.__name__} instances, "
                        f"got {type(item)}."
                    )

    # -----------------------------------------------------------------------
    # Convenience factory method
    # -----------------------------------------------------------------------

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Project:
        """
        Build a Project instance from a dictionary (e.g., parsed YAML/JSON).

        Performs validation during construction and raises
        ProjectValidationError if the data is invalid.

        Parameters
        ----------
        data : Dict[str, Any]
            Dictionary representation of the project configuration.

        Returns
        -------
        Project
            Fully validated Project instance.

        Raises
        ------
        ProjectValidationError
            If the configuration data fails any validation check.
        """
        # Safety: work on a copy
        data = data.copy()

        def extract_authors(authors_raw: Any) -> List[Author]:
            """Convert raw author entries (dict or string) to Author objects."""
            authors: List[Author] = []
            if not authors_raw:
                return authors
            if not isinstance(authors_raw, (list, tuple)):
                raise ProjectValidationError("'authors' must be a list.")

            for entry in authors_raw:
                if isinstance(entry, str):
                    # Format: "Name <email>" or just "Name"
                    match = re.match(r"(.+?)\s*<([^>]+)>", entry)
                    if match:
                        authors.append(Author(name=match.group(1), email=match.group(2)))
                    else:
                        authors.append(Author(name=entry.strip()))
                elif isinstance(entry, dict):
                    authors.append(Author(
                        name=entry.get("name", ""),
                        email=entry.get("email")
                    ))
                else:
                    raise ProjectValidationError(
                        "Each author entry must be a string or a dict."
                    )
            return authors

        def extract_dependencies(
            deps_raw: Any, dep_type: DependencyType = DependencyType.PRODUCTION
        ) -> List[Dependency]:
            """Convert raw dependency entries (dict or list of strings) to Dependency objects."""
            deps: List[Dependency] = []
            if not deps_raw:
                return deps
            if isinstance(deps_raw, dict):
                # {name: version} format
                for name, version in deps_raw.items():
                    deps.append(Dependency(
                        name=name,
                        version=version if version else None,
                        type=dep_type
                    ))
            elif isinstance(deps_raw, list):
                for item in deps_raw:
                    if isinstance(item, str):
                        # "name==version" or just "name"
                        parts = re.split(r"==|>=|<=|!=|~=|@", item, maxsplit=1)
                        name = parts[0].strip()
                        version = parts[1].strip() if len(parts) > 1 else None
                        deps.append(Dependency(name=name, version=version, type=dep_type))
                    elif isinstance(item, dict):
                        deps.append(Dependency(
                            name=item.get("name", ""),
                            version=item.get("version"),
                            type=dep_type
                        ))
                    else:
                        raise ProjectValidationError(
                            "Each dependency entry must be a string or a dict."
                        )
            else:
                raise ProjectValidationError(
                    f"Dependencies must be a dict or list, got {type(deps_raw)}."
                )
            return deps

        def extract_scripts(scripts_raw: Any) -> List[Script]:
            """Convert raw scripts (dict) to Script objects."""
            scripts: List[Script] = []
            if not scripts_raw:
                return scripts
            if not isinstance(scripts_raw, dict):
                raise ProjectValidationError("'scripts' must be a dict.")

            for name, command in scripts_raw.items():
                description = None
                if isinstance(command, dict):
                    description = command.get("description")
                    command = command.get("command", "")
                scripts.append(Script(
                    name=name,
                    command=command,
                    description=description
                ))
            return scripts

        def extract_paths(paths_raw: Any) -> PathConfig:
            """Convert raw paths (dict) to PathConfig."""
            if not paths_raw:
                return PathConfig()
            if not isinstance(paths_raw, dict):
                raise ProjectValidationError("'paths' must be a dict.")
            # Convert string values to Path
            cleaned = {}
            for key, value in paths_raw.items():
                cleaned[key] = Path(value) if isinstance(value, str) else value
            return PathConfig(**cleaned)

        def extract_python(python_raw: Any) -> PythonSettings:
            """Convert raw python settings (dict) to PythonSettings."""
            if not python_raw:
                return PythonSettings()
            if not isinstance(python_raw, dict):
                raise ProjectValidationError("'python' must be a dict.")
            return PythonSettings(**python_raw)

        # --- Main construction ---
        metadata = data.pop("metadata", data)  # Allow top‑level or nested
        if "name" not in metadata:
            raise ProjectValidationError("Project must have a 'name'.")

        project = cls(
            metadata=ProjectMetadata(
                name=metadata.get("name", ""),
                version=metadata.get("version", "0.1.0"),
                description=metadata.get("description", ""),
                license=metadata.get("license"),
                authors=extract_authors(metadata.get("authors", [])),
            ),
            dependencies=extract_dependencies(
                data.pop("dependencies", []), DependencyType.PRODUCTION
            ),
            dev_dependencies=extract_dependencies(
                data.pop("dev_dependencies", []), DependencyType.DEVELOPMENT
            ),
            scripts=extract_scripts(data.pop("scripts", {})),
            paths=extract_paths(data.pop("paths", {})),
            python=extract_python(data.pop("python", {})),
            custom=data.pop("custom", data),  # Remaining keys become custom
        )
        return project

    # -----------------------------------------------------------------------
    # Utility methods
    # -----------------------------------------------------------------------

    def all_dependencies(self) -> List[Dependency]:
        """Return production and development dependencies combined."""
        return list(self.dependencies) + list(self.dev_dependencies)

    def has_dependency(self, name: str) -> bool:
        """Check if a dependency with the given name exists (any type)."""
        name = name.strip()
        return any(dep.name == name for dep in self.all_dependencies())

    def get_script(self, name: str) -> Optional[Script]:
        """Retrieve a script by name, or None if not found."""
        for script in self.scripts:
            if script.name == name:
                return script
        return None