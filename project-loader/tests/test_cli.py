"""Tests for the CLI commands using Click testing utilities."""
import json
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
import yaml
from click.testing import CliRunner

# Assuming the CLI entry point is `cli` from `project_loader.cli`
from project_loader.cli import cli


@pytest.fixture
def runner():
    """Provide a Click CliRunner for testing."""
    return CliRunner()


@pytest.fixture
def valid_config_yaml():
    """Return a valid YAML configuration string for testing."""
    return yaml.dump({
        "projects": [
            {
                "name": "alpha",
                "path": "/path/to/alpha",
                "description": "First project"
            },
            {
                "name": "beta",
                "path": "/path/to/beta",
                "description": "Second project"
            }
        ]
    })


@pytest.fixture
def valid_config_json():
    """Return a valid JSON configuration string for testing."""
    return json.dumps({
        "projects": [
            {
                "name": "gamma",
                "path": "/path/to/gamma",
                "description": "Third project"
            }
        ]
    })


@pytest.fixture
def invalid_yaml():
    """Return an invalid YAML string."""
    return "projects: [unclosed list"


@pytest.fixture
def empty_config():
    """Return an empty project list configuration."""
    return yaml.dump({"projects": []})


def _create_config_file(tmp_path, content, filename="config.yaml"):
    """Helper to write a config file inside a temporary directory."""
    config_path = tmp_path / filename
    config_path.write_text(content)
    return str(config_path)


# -----------------------------------------------------------------------------
# Help & Metadata
# -----------------------------------------------------------------------------

class TestHelp:
    """Test the help output of the CLI."""

    def test_help_returns_zero_exit_code(self, runner):
        """Running with --help should exit with code 0."""
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0

    def test_help_contains_command_names(self, runner):
        """Help text should mention expected commands."""
        result = runner.invoke(cli, ["--help"])
        assert "load" in result.output
        assert "list" in result.output

    def test_subcommand_help(self, runner):
        """Each subcommand should have its own help."""
        for cmd in ("load", "list"):
            result = runner.invoke(cli, [cmd, "--help"])
            assert result.exit_code == 0
            assert cmd in result.output


# -----------------------------------------------------------------------------
# List Command
# -----------------------------------------------------------------------------

class TestListCommand:
    """Test the `list` command of the CLI."""

    def test_list_all_projects(self, runner, tmp_path, valid_config_yaml):
        """List all projects from a valid YAML config."""
        config_path = _create_config_file(tmp_path, valid_config_yaml)
        result = runner.invoke(cli, ["list", "--config", config_path])
        assert result.exit_code == 0
        assert "alpha" in result.output
        assert "beta" in result.output
        assert "/path/to/alpha" in result.output

    def test_list_with_json_config(self, runner, tmp_path, valid_config_json):
        """List projects from a valid JSON config file."""
        config_path = _create_config_file(tmp_path, valid_config_json, filename="config.json")
        result = runner.invoke(cli, ["list", "--config", config_path])
        assert result.exit_code == 0
        assert "gamma" in result.output
        assert "/path/to/gamma" in result.output

    def test_list_empty_config(self, runner, tmp_path, empty_config):
        """List should handle empty project list gracefully."""
        config_path = _create_config_file(tmp_path, empty_config)
        result = runner.invoke(cli, ["list", "--config", config_path])
        assert result.exit_code == 0
        # Should print a message like "No projects found" or just nothing
        # Check for empty table or appropriate message
        assert "No projects" in result.output or result.output.strip() == ""

    def test_list_missing_config(self, runner):
        """List without a config file should error."""
        result = runner.invoke(cli, ["list"])
        assert result.exit_code != 0
        assert "Missing option" in result.output or "--config" in result.output

    def test_list_nonexistent_config(self, runner):
        """List with a nonexistent config file should error."""
        result = runner.invoke(cli, ["list", "--config", "/nonexistent/path.yaml"])
        assert result.exit_code != 0
        assert "Error" in result.output or "does not exist" in result.output

    def test_list_invalid_yaml(self, runner, tmp_path, invalid_yaml):
        """List with invalid YAML should produce an error."""
        config_path = _create_config_file(tmp_path, invalid_yaml)
        result = runner.invoke(cli, ["list", "--config", config_path])
        assert result.exit_code != 0
        # Should mention YAML parsing error
        assert "YAML" in result.output or "parse" in result.output or "Error" in result.output

    def test_list_with_format_option(self, runner, tmp_path, valid_config_yaml):
        """Support an optional --format flag (e.g. table, json, yaml)."""
        config_path = _create_config_file(tmp_path, valid_config_yaml)
        for fmt in ("json", "yaml"):
            result = runner.invoke(cli, ["list", "--config", config_path, "--format", fmt])
            assert result.exit_code == 0, f"Failed for format {fmt}: {result.output}"
            if fmt == "json":
                # Output should be valid JSON
                try:
                    json.loads(result.output)
                except json.JSONDecodeError:
                    pytest.fail(f"Output is not valid JSON: {result.output}")
            elif fmt == "yaml":
                # Output should be valid YAML
                try:
                    yaml.safe_load(result.output)
                except yaml.YAMLError:
                    pytest.fail(f"Output is not valid YAML: {result.output}")

    def test_list_with_filter(self, runner, tmp_path, valid_config_yaml):
        """List with a --filter option (basic name matching)."""
        config_path = _create_config_file(tmp_path, valid_config_yaml)
        result = runner.invoke(cli, ["list", "--config", config_path, "--filter", "alpha"])
        assert result.exit_code == 0
        assert "alpha" in result.output
        assert "beta" not in result.output  # filter should exclude beta

    def test_list_verbose(self, runner, tmp_path, valid_config_yaml):
        """List with --verbose should show extra details."""
        config_path = _create_config_file(tmp_path, valid_config_yaml)
        result = runner.invoke(cli, ["list", "--config", config_path, "--verbose"])
        assert result.exit_code == 0
        # Verbose may show full paths, descriptions, etc.
        assert "First project" in result.output or "description" in result.output


# -----------------------------------------------------------------------------
# Load Command
# -----------------------------------------------------------------------------

class TestLoadCommand:
    """Test the `load` command of the CLI."""

    def test_load_single_project(self, runner, tmp_path, valid_config_yaml):
        """Load a specific project by name."""
        config_path = _create_config_file(tmp_path, valid_config_yaml)
        result = runner.invoke(cli, ["load", "alpha", "--config", config_path])
        assert result.exit_code == 0
        assert "alpha" in result.output
        assert "loaded" in result.output.lower()

    def test_load_all_projects(self, runner, tmp_path, valid_config_yaml):
        """Load all projects (no name argument)."""
        config_path = _create_config_file(tmp_path, valid_config_yaml)
        result = runner.invoke(cli, ["load", "--config", config_path])
        assert result.exit_code == 0
        assert "alpha" in result.output
        assert "beta" in result.output

    def test_load_missing_config(self, runner):
        """Load without config file should error."""
        result = runner.invoke(cli, ["load"])
        assert result.exit_code != 0
        assert "Missing option" in result.output or "--config" in result.output

    def test_load_nonexistent_project(self, runner, tmp_path, valid_config_yaml):
        """Load a project name that does not exist."""
        config_path = _create_config_file(tmp_path, valid_config_yaml)
        result = runner.invoke(cli, ["load", "nonexistent", "--config", config_path])
        assert result.exit_code != 0
        assert "not found" in result.output.lower() or "error" in result.output.lower()

    def test_load_empty_config(self, runner, tmp_path, empty_config):
        """Load from an empty config should handle gracefully."""
        config_path = _create_config_file(tmp_path, empty_config)
        result = runner.invoke(cli, ["load", "--config", config_path])
        assert result.exit_code == 0
        # Should indicate no projects to load
        assert "no projects" in result.output.lower() or "nothing" in result.output.lower()

    def test_load_uses_default_config(self, runner, tmp_path, valid_config_yaml):
        """If no --config provided, maybe it looks for a default file (e.g. project-loader.yaml)."""
        # Create default config in current directory (runner uses isolated filesystem)
        default_config = "project-loader.yaml"
        with runner.isolated_filesystem():
            Path(default_config).write_text(valid_config_yaml)
            result = runner.invoke(cli, ["load"])
            assert result.exit_code == 0
            assert "alpha" in result.output

    def test_load_verbose(self, runner, tmp_path, valid_config_yaml):
        """Load with --verbose should print detailed loading steps."""
        config_path = _create_config_file(tmp_path, valid_config_yaml)
        result = runner.invoke(cli, ["load", "--config", config_path, "--verbose"])
        assert result.exit_code == 0
        # Verbose output should contain additional info
        assert "Loading" in result.output or "loaded" in result.output.lower()


# -----------------------------------------------------------------------------
# Advanced / Negative Tests
# -----------------------------------------------------------------------------

class TestErrorHandling:
    """Test edge cases and error handling."""

    def test_no_command(self, runner):
        """CLI with no command should error or show help."""
        result = runner.invoke(cli, [])
        # exit code non-zero because no subcommand
        assert result.exit_code != 0
        # Should suggest available commands
        assert "Usage" in result.output

    def test_invalid_subcommand(self, runner):
        """An unknown subcommand should error."""
        result = runner.invoke(cli, ["foobar"])
        assert result.exit_code != 0
        assert "No such command" in result.output

    def test_unsupported_config_format(self, runner, tmp_path):
        """Config with an unsupported extension should raise an error."""
        config_path = str(tmp_path / "config.toml")
        Path(config_path).write_text("some content")
        result = runner.invoke(cli, ["list", "--config", config_path])
        assert result.exit_code != 0
        assert "format" in result.output.lower() or "unsupported" in result.output.lower()

    @pytest.mark.skipif(not yaml, reason="yaml library not available")
    def test_yaml_not_installed(self, runner, tmp_path, valid_config_yaml):
        """If PyYAML is not installed, the tool should give a clear error."""
        config_path = _create_config_file(tmp_path, valid_config_yaml)
        with patch("project_loader.cli.yaml", None):  # simulate missing yaml
            result = runner.invoke(cli, ["list", "--config", config_path])
            assert result.exit_code != 0
            assert "install" in result.output.lower() or "yaml" in result.output.lower()

    def test_permission_error(self, runner, tmp_path):
        """Config file with no read permission should error."""
        config_path = tmp_path / "secret.yaml"
        config_path.write_text("key: value")
        config_path.chmod(0o000)  # remove all permissions
        result = runner.invoke(cli, ["list", "--config", str(config_path)])
        assert result.exit_code != 0
        # Should mention permission or denied
        assert "permission" in result.output.lower() or "denied" in result.output.lower()

    def test_config_file_is_directory(self, runner, tmp_path):
        """Config path pointing to a directory should error."""
        result = runner.invoke(cli, ["list", "--config", str(tmp_path)])
        assert result.exit_code != 0
        assert "directory" in result.output.lower() or "is a directory" in result.output.lower()


# -----------------------------------------------------------------------------
# Configuration parsing edge cases
# -----------------------------------------------------------------------------

class TestConfigParsing:
    """Test various valid and invalid configuration structures."""

    def test_config_with_missing_projects_key(self, runner, tmp_path):
        """Config missing the 'projects' key should error gracefully."""
        bad_config = yaml.dump({"not_projects": []})
        config_path = _create_config_file(tmp_path, bad_config)
        result = runner.invoke(cli, ["list", "--config", config_path])
        assert result.exit_code != 0
        assert "projects" in result.output.lower()

    def test_config_with_nested_projects(self, runner, tmp_path):
        """Projects list containing invalid entries (e.g. strings) should warn or error."""
        bad_projects = yaml.dump({"projects": ["not_a_dict"]})
        config_path = _create_config_file(tmp_path, bad_projects)
        result = runner.invoke(cli, ["list", "--config", config_path])
        # Should either skip invalid entries or raise an error
        assert result.exit_code == 0 or result.exit_code != 0
        # If it skips, output should at least note the problem
        if result.exit_code == 0:
            assert "invalid" in result.output.lower() or "skip" in result.output.lower()
        else:
            assert "error" in result.output.lower()

    def test_config_duplicate_project_names(self, runner, tmp_path):
        """Projects with duplicate names should be handled (merged or error)."""
        duplicate = yaml.dump({
            "projects": [
                {"name": "dup", "path": "/a"},
                {"name": "dup", "path": "/b"}
            ]
        })
        config_path = _create_config_file(tmp_path, duplicate)
        result = runner.invoke(cli, ["list", "--config", config_path])
        # Should succeed but maybe warn or show one entry
        assert result.exit_code == 0
        # The output should contain "dup" at least once
        assert result.output.count("dup") >= 1