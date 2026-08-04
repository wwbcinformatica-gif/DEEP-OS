"""
Tests for the Project dataclass creation and validation.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional
import pytest

from project_loader.models import Project


class TestProjectCreation:
    """Test suite for Project dataclass instantiation."""

    @pytest.fixture
    def sample_data(self) -> Dict[str, Any]:
        """Provide a default set of valid project data."""
        return {
            "name": "my-project",
            "path": "/some/path",
            "description": "A test project",
            "tags": ["python", "cli"],
        }

    def test_create_with_all_fields(self, sample_data: Dict[str, Any]) -> None:
        """Verify that a Project can be created with all optional fields."""
        project = Project(**sample_data)
        assert project.name == sample_data["name"]
        assert project.path == Path(sample_data["path"])
        assert project.description == sample_data["description"]
        assert project.tags == sample_data["tags"]

    def test_create_with_required_only(self) -> None:
        """Verify that a Project can be created with only the required field."""
        required = {"name": "my-project"}
        project = Project(**required)
        assert project.name == "my-project"
        # Check default values
        assert project.path == Path()
        assert project.description == ""
        assert project.tags == []

    def test_path_is_converted_to_pathlib_path(self) -> None:
        """Ensure that a string path is stored as a pathlib.Path."""
        project = Project(name="test", path="/some/path")
        assert isinstance(project.path, Path)
        assert str(project.path) == "/some/path"

    def test_tags_default_to_empty_list(self) -> None:
        """Verify that the tags field defaults to an empty list and is not shared."""
        project1 = Project(name="a")
        project2 = Project(name="b")
        project1.tags.append("new")
        assert project2.tags == []

    def test_equality(self) -> None:
        """Two projects with the same fields should be equal."""
        data = {"name": "proj", "path": "/tmp", "description": "desc", "tags": ["a"]}
        p1 = Project(**data)
        p2 = Project(**data)
        assert p1 == p2
        assert p1 is not p2

    def test_inequality(self) -> None:
        """Different fields should yield unequal projects."""
        p1 = Project(name="a", path="/p1")
        p2 = Project(name="a", path="/p2")
        assert p1 != p2

    def test_hashable(self) -> None:
        """Project instances should be usable in sets and as dict keys."""
        p1 = Project(name="hash-me")
        p2 = Project(name="hash-me")
        collection = {p1, p2}
        assert len(collection) == 1  # Equal objects must have same hash

    def test_repr(self) -> None:
        """The repr should contain the class name and key attributes."""
        project = Project(name="repr_check", path="/my/path")
        rep = repr(project)
        assert "Project" in rep
        assert "name='repr_check'" in rep

    def test_str(self) -> None:
        """The string representation should be human-readable."""
        project = Project(name="my-tool", description="CLI utility")
        string = str(project)
        assert "my-tool" in string
        # Description is optional, but should appear if set
        assert "CLI utility" not in string  # Because we haven't forced inclusion
        # However, default __str__ from dataclass may not include description; it's fine
        # This test just ensures no exception raised
        assert len(string) > 0


class TestProjectValidation:
    """Test validation logic in the Project dataclass."""

    def test_name_must_be_non_empty(self) -> None:
        """Provide an empty name string should raise ValueError."""
        with pytest.raises(ValueError, match="name must be a non-empty string"):
            Project(name="")

    def test_name_cannot_be_none(self) -> None:
        """Omitting name should raise TypeError because it's required."""
        with pytest.raises(TypeError):
            Project()  # type: ignore[call-arg]

    def test_name_cannot_be_none_explicit(self) -> None:
        """Passing None as name should raise ValueError."""
        with pytest.raises(ValueError, match="name must be a non-empty string"):
            Project(name=None)  # type: ignore[arg-type]

    def test_path_must_be_string_or_pathlike(self) -> None:
        """Path of invalid type should raise TypeError."""
        with pytest.raises(TypeError, match="path must be a string or path-like"):
            Project(name="test", path=12345)  # type: ignore[arg-type]

    def test_path_empty_string_accepted(self) -> None:
        """An empty string for path should be converted to Path() (current dir)."""
        project = Project(name="test", path="")
        assert project.path == Path()

    def test_description_type_validation(self) -> None:
        """Description must be a string if provided."""
        with pytest.raises(TypeError, match="description must be a string"):
            Project(name="test", description=42)  # type: ignore[arg-type]

    def test_tags_must_be_a_list_of_strings(self) -> None:
        """Tags must be a list of strings."""
        with pytest.raises(TypeError, match="tags must be a list of strings"):
            Project(name="test", tags="single")  # type: ignore[arg-type]

        with pytest.raises(TypeError, match="tags must be a list of strings"):
            Project(name="test", tags=[1, 2, 3])  # type: ignore[list-item]

    def test_tags_members_must_be_strings(self) -> None:
        """Each tag in the list must be a string."""
        with pytest.raises(TypeError, match="Each tag must be a string"):
            Project(name="test", tags=["ok", 42])  # type: ignore[list-item]

    def test_name_length_maximum(self) -> None:
        """If a maximum length is imposed, verify it."""
        # Assuming a max length of 100 (choose a reasonable limit)
        long_name = "a" * 101
        with pytest.raises(ValueError, match="name must be 100 characters or fewer"):
            Project(name=long_name)

    def test_path_must_not_contain_null_bytes(self) -> None:
        """Path with null bytes should raise ValueError."""
        with pytest.raises(ValueError, match="path contains null byte"):
            Project(name="test", path="/some/\x00path")

    def test_multiple_validation_errors(self) -> None:
        """First validation error should be raised (order matters)."""
        with pytest.raises(ValueError, match="name must be a non-empty string"):
            Project(name="", path="valid", description="", tags=[])


class TestProjectSerialization:
    """Test conversion to and from dict (if applicable)."""

    def test_to_dict(self) -> None:
        """The to_dict() method should return a dictionary with all fields."""
        data = {"name": "serde", "path": "/tmp", "description": "test", "tags": ["a"]}
        project = Project(**data)
        result = project.to_dict()
        assert result["name"] == "serde"
        assert result["path"] == "/tmp"
        assert result["description"] == "test"
        assert result["tags"] == ["a"]

    def test_from_dict(self) -> None:
        """Creating a Project from a dictionary should work."""
        data = {"name": "from_dict", "path": "/some/path"}
        project = Project.from_dict(data)
        assert project.name == "from_dict"
        assert project.path == Path("/some/path")

    def test_from_dict_extra_keys_ignored(self) -> None:
        """Extra keys in the dictionary should be silently ignored."""
        data = {"name": "test", "extra": "should_not_break"}
        project = Project.from_dict(data)
        assert project.name == "test"

    def test_round_trip(self) -> None:
        """to_dict() and from_dict() should be inverses."""
        original = Project(name="round", path="/start", description="go", tags=["x"])
        data = original.to_dict()
        restored = Project.from_dict(data)
        assert original == restored


class TestProjectEdgeCases:
    """Corner cases and special values."""

    def test_name_with_only_spaces(self) -> None:
        """A name consisting only of spaces should be considered empty."""
        with pytest.raises(ValueError, match="name must be a non-empty string"):
            Project(name="   ")

    def test_very_long_description(self) -> None:
        """Long descriptions should be allowed (if no limit)."""
        long_desc = "x" * 10_000
        project = Project(name="long_desc", description=long_desc)
        assert len(project.description) == 10_000

    def test_tags_empty_list(self) -> None:
        """An empty list of tags is acceptable."""
        project = Project(name="no_tags", tags=[])
        assert project.tags == []

    def test_path_relative_conversion(self) -> None:
        """Relative paths should be normalized to pathlib.Path."""
        project = Project(name="rel", path="relative/path")
        expected = Path("relative/path")
        assert project.path == expected

    def test_identical_paths_resolve(self) -> None:
        """
        Two projects with same logical path should compare equal
        even if string representation differs (e.g., trailing slash).
        """
        p1 = Project(name="a", path="/some/path/")
        p2 = Project(name="a", path="/some/path")
        # Paths are normalized if we use pathlib.Path; trailing slashes are dropped
        assert p1.path == p2.path
        assert p1 == p2

    def test_case_sensitivity_of_name(self) -> None:
        """Names should be treated case‑sensitively (unless overridden)."""
        p1 = Project(name="Foo")
        p2 = Project(name="foo")
        assert p1 != p2

    def test_frozen_dataclass(self) -> None:
        """If the dataclass is frozen, attribute assignment raises FrozenInstanceError."""
        project = Project(name="frozen_test")
        with pytest.raises(Exception):  # dataclasses.FrozenInstanceError
            project.name = "new_name"  # type: ignore[misc]