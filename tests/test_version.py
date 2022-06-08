"""Provide tests for project version."""
from proman.versioning import __version__


def test_version() -> None:
    """Test project metadata version."""
    assert __version__ == '0.6.1a0'
