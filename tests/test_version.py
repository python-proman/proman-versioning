'''Provide tests for project version.'''
from proman_releases import __version__


def test_version():
    '''Test project metadata version.'''
    assert __version__ == "0.1.0"
