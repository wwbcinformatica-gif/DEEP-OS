import pytest
from pathlib import Path
from lister import get_folders


# -----------------------------------------------------------------------------
# Fixtures
# -----------------------------------------------------------------------------

@pytest.fixture
def temp_dir_with_subdirs(tmp_path: Path) -> Path:
    """Create a temporary directory with a known set of subdirectories and a file."""
    dirs = ["src", "docs", "tests", "src/utils", "docs/api"]
    for d in dirs:
        (tmp_path / d).mkdir(parents=True, exist_ok=True)
    # Create a regular file that should NOT appear in the result
    (tmp_path / "readme.md").touch()
    # Create a hidden directory (starts with a dot)
    (tmp_path / ".hidden").mkdir()
    return tmp_path


@pytest.fixture
def empty_dir(tmp_path: Path) -> Path:
    """Return an empty directory (no children at all)."""
    return tmp_path


# -----------------------------------------------------------------------------
# Tests for normal scenarios
# -----------------------------------------------------------------------------

class TestGetFoldersNormal:
    """Tests with a well-structured directory."""

    def test_returns_only_directories(self, temp_dir_with_subdirs: Path):
        """get_folders should return only directories, not files."""
        result = get_folders(temp_dir_with_subdirs)
        # All returned items should exist and be directories
        for item in result:
            full_path = Path(item)
            assert full_path.exists(), f"Item does not exist: {item}"
            assert full_path.is_dir(), f"Item is not a directory: {item}"

    def test_includes_all_subdirectories(self, temp_dir_with_subdirs: Path):
        """All immediate subdirectories must be present in the result."""
        result = get_folders(temp_dir_with_subdirs)
        result_names = {Path(p).name for p in result}
        expected = {"src", "docs", "tests", ".hidden"}
        assert expected.issubset(result_names), (
            f"Missing expected directories. Expected: {expected}, Got: {result_names}"
        )

    def test_does_not_include_files(self, temp_dir_with_subdirs: Path):
        """Regular files (e.g., readme.md) must NOT be returned."""
        result = get_folders(temp_dir_with_subdirs)
        result_names = {Path(p).name for p in result}
        assert "readme.md" not in result_names

    def test_returns_path_type(self, temp_dir_with_subdirs: Path):
        """Each item should be a string or Path (consistent with implementation)."""
        result = get_folders(temp_dir_with_subdirs)
        if result:
            first = result[0]
            assert isinstance(first, (str, Path)), (
                f"Items should be str or Path, got {type(first).__name__}"
            )


class TestGetFoldersEmpty:
    """Tests when the directory contains no subdirectories."""

    def test_empty_directory(self, empty_dir: Path):
        """An empty directory should produce an empty list."""
        result = get_folders(empty_dir)
        assert result == [], f"Expected empty list, got {result}"

    def test_directory_with_only_files(self, tmp_path: Path):
        """Directory with only files, no subdirectories, should return empty list."""
        (tmp_path / "file1.txt").touch()
        (tmp_path / "file2.txt").touch()
        result = get_folders(tmp_path)
        assert result == []

    def test_directory_with_hidden_file_only(self, tmp_path: Path):
        """Hidden files (dot files) are not directories – should still return empty."""
        (tmp_path / ".config").touch()
        result = get_folders(tmp_path)
        assert result == []


# -----------------------------------------------------------------------------
# Tests for invalid paths
# -----------------------------------------------------------------------------

class TestGetFoldersInvalidPaths:
    """Tests when the path does not exist or is not a directory."""

    def test_non_existent_path(self, tmp_path: Path):
        """A path that does not exist should raise FileNotFoundError."""
        non_existent = tmp_path / "does_not_exist"
        with pytest.raises(FileNotFoundError):
            get_folders(non_existent)

    def test_file_path(self, tmp_path: Path):
        """A file path (not a directory) should raise NotADirectoryError or equivalent."""
        file_path = tmp_path / "some_file.txt"
        file_path.touch()
        with pytest.raises((NotADirectoryError, FileNotFoundError)):
            # Some implementations may raise FileNotFoundError if they try to list it.
            # Accept both for robustness.
            get_folders(file_path)

    def test_path_is_none(self):
        """Passing None should raise TypeError or similar."""
        with pytest.raises(TypeError):
            get_folders(None)

    def test_empty_string(self, tmp_path: Path):
        """An empty string path should raise FileNotFoundError (or ValueError)."""
        with pytest.raises((FileNotFoundError, ValueError)):
            get_folders("")

    def test_path_is_relative_broken_symlink(self, tmp_path: Path):
        """A broken symlink should be handled as a non-existent path."""
        link_path = tmp_path / "broken_link"
        link_path.symlink_to(tmp_path / "nonexistent_target")
        # Depending on implementation, this may raise FileNotFoundError or similar.
        with pytest.raises(FileNotFoundError):
            get_folders(link_path)

    def test_path_with_permission_denied(self, tmp_path: Path):
        """A directory without read permission should raise PermissionError."""
        restricted_dir = tmp_path / "restricted"
        restricted_dir.mkdir()
        # Remove read permission – only works on Unix-like systems.
        restricted_dir.chmod(0o000)
        try:
            with pytest.raises(PermissionError):
                get_folders(restricted_dir)
        finally:
            # Restore permissions so cleanup can happen
            restricted_dir.chmod(0o755)


# -----------------------------------------------------------------------------
# Additional edge cases
# -----------------------------------------------------------------------------

class TestGetFoldersEdgeCases:
    """Other potential edge cases."""

    def test_unicode_directory_names(self, tmp_path: Path):
        """Non‐ASCII (Unicode) directory names must be supported."""
        unicode_dir = tmp_path / "résumé"
        unicode_dir.mkdir()
        result = get_folders(tmp_path)
        assert any("résumé" in str(p) for p in result), (
            f"Unicode directory not found in result: {result}"
        )

    def test_many_directories_performance(self, tmp_path: Path):
        """Large number of directories should not crash (smoke test)."""
        for i in range(1000):
            (tmp_path / f"dir_{i}").mkdir()
        result = get_folders(tmp_path)
        assert len(result) >= 1000

    def test_pathlib_path_input(self, tmp_path: Path):
        """The function should accept a Path object."""
        (tmp_path / "subdir").mkdir()
        result = get_folders(tmp_path)
        assert isinstance(result, list)

    def test_recursive_directories_arent_returned(self, tmp_path: Path):
        """Only immediate subdirectories should be listed, not deeply nested ones."""
        (tmp_path / "a" / "b" / "c").mkdir(parents=True)
        result = get_folders(tmp_path)
        result_names = {Path(p).name for p in result}
        assert "a" in result_names
        assert "b" not in result_names  # b is inside a, not immediate
        assert "c" not in result_names