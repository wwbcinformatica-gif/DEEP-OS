import json
import pytest
from pathlib import Path
from typing import Any, Dict, List
from unittest.mock import mock_open, patch

from project_loader.loader import Loader, ProjectNotFoundError, ConfigError


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def valid_config_data() -> List[Dict[str, Any]]:
    """Return a sample list of projects as would be stored in a config file."""
    return [
        {
            "name": "alpha",
            "path": "/home/user/projects/alpha",
            "description": "Alpha project",
        },
        {
            "name": "beta",
            "path": "/home/user/projects/beta",
            "description": "Beta project",
        },
    ]


@pytest.fixture
def valid_config_json(tmp_path: Path, valid_config_data: List[Dict[str, Any]]) -> Path:
    """Create a temporary JSON config file with valid project data."""
    config_file = tmp_path / "projects.json"
    config_file.write_text(json.dumps(valid_config_data), encoding="utf-8")
    return config_file


@pytest.fixture
def empty_config(tmp_path: Path) -> Path:
    """Create an empty JSON file."""
    config_file = tmp_path / "empty.json"
    config_file.write_text("[]", encoding="utf-8")
    return config_file


@pytest.fixture
def malformed_config(tmp_path: Path) -> Path:
    """Create a malformed (non-JSON) config file."""
    config_file = tmp_path / "malformed.txt"
    config_file.write_text("this is not json", encoding="utf-8")
    return config_file


@pytest.fixture
def missing_field_config(tmp_path: Path) -> Path:
    """Create a config where one project is missing the required 'path' field."""
    data = [
        {"name": "incomplete", "description": "No path given"},
    ]
    config_file = tmp_path / "missing_field.json"
    config_file.write_text(json.dumps(data), encoding="utf-8")
    return config_file


# ---------------------------------------------------------------------------
# Test class
# ---------------------------------------------------------------------------

class TestLoadProject:
    """Tests for Loader.load_project with valid and invalid inputs."""

    def test_load_existing_project(
        self, valid_config_json: Path, valid_config_data: List[Dict[str, Any]]
    ) -> None:
        """Should return the project data for a known project name."""
        loader = Loader(valid_config_json)
        project = loader.load_project("alpha")
        assert project == valid_config_data[0]

    def test_load_project_case_sensitive(
        self, valid_config_json: Path
    ) -> None:
        """Project names should be case-sensitive."""
        loader = Loader(valid_config_json)
        with pytest.raises(ProjectNotFoundError):
            loader.load_project("Alpha")

    def test_load_nonexistent_project(self, valid_config_json: Path) -> None:
        """Should raise ProjectNotFoundError for an unknown project."""
        loader = Loader(valid_config_json)
        with pytest.raises(ProjectNotFoundError, match="not found"):
            loader.load_project("nonexistent")

    def test_load_from_empty_config(self, empty_config: Path) -> None:
        """Should raise ProjectNotFoundError when config has no projects."""
        loader = Loader(empty_config)
        with pytest.raises(ProjectNotFoundError):
            loader.load_project("alpha")

    def test_load_project_multiple_calls(
        self, valid_config_json: Path, valid_config_data: List[Dict[str, Any]]
    ) -> None:
        """Loader should support loading multiple projects from the same config."""
        loader = Loader(valid_config_json)
        assert loader.load_project("alpha") == valid_config_data[0]
        assert loader.load_project("beta") == valid_config_data[1]

    def test_file_not_found(self) -> None:
        """Should raise FileNotFoundError when config file does not exist."""
        loader = Loader(Path("/nonexistent/path/config.json"))
        with pytest.raises(FileNotFoundError):
            loader.load_project("any")

    def test_malformed_json(self, malformed_config: Path) -> None:
        """Should raise ConfigError for malformed JSON content."""
        loader = Loader(malformed_config)
        with pytest.raises(ConfigError, match="failed to parse config"):
            loader.load_project("alpha")

    def test_missing_required_field(self, missing_field_config: Path) -> None:
        """Should raise ConfigError if a project is missing a mandatory field."""
        loader = Loader(missing_field_config)
        with pytest.raises(ConfigError, match="missing required field"):
            loader.load_project("incomplete")

    def test_load_project_as_dict(self, valid_config_json: Path) -> None:
        """Return value should be a dictionary with expected keys."""
        loader = Loader(valid_config_json)
        project = loader.load_project("alpha")
        assert isinstance(project, dict)
        assert set(project.keys()) == {"name", "path", "description"}

    def test_load_project_empty_name(self, valid_config_json: Path) -> None:
        """Should handle empty project name appropriately (error or valid)."""
        loader = Loader(valid_config_json)
        # Depending on design, empty name might be invalid or a valid project name.
        # We'll check that it raises an error if empty or not found.
        with pytest.raises(ProjectNotFoundError):
            loader.load_project("")

    @patch("pathlib.Path.read_text", side_effect=PermissionError("Permission denied"))
    def test_permission_error(self, mock_read: Any, tmp_path: Path) -> None:
        """Should raise an appropriate error when config file is not readable."""
        config_path = tmp_path / "secret.json"
        loader = Loader(config_path)
        with pytest.raises(PermissionError):
            loader.load_project("alpha")

    def test_config_with_extra_fields(self, tmp_path: Path) -> None:
        """Extra fields in a project entry should be tolerated."""
        data = [
            {
                "name": "extra",
                "path": "/tmp/extra",
                "description": "Extra field project",
                "version": "2.0",
            }
        ]
        config_file = tmp_path / "extra.json"
        config_file.write_text(json.dumps(data), encoding="utf-8")
        loader = Loader(config_file)
        project = loader.load_project("extra")
        assert project["name"] == "extra"
        assert "version" in project  # extra fields preserved

    def test_integration_with_real_file(self, tmp_path: Path) -> None:
        """Full integration: create config, load project, verify structure."""
        config = tmp_path / "my_projects.json"
        config.write_text(
            json.dumps([
                {"name": "webapp", "path": "/var/www/webapp", "description": "Main web application"},
            ]),
            encoding="utf-8",
        )
        loader = Loader(config)
        proj = loader.load_project("webapp")
        assert proj == {
            "name": "webapp",
            "path": "/var/www/webapp",
            "description": "Main web application",
        }