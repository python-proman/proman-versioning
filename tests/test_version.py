"""Provide tests for project version."""
from versioning import __version__


def test_version() -> None:
    """Test project metadata version."""
    assert __version__ == '0.4.0a2'
