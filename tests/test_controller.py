# type: ignore
"""Test git hooks pipeline."""

import os
from unittest.mock import Mock, mock_open, patch

from versioning import ReleaseController, Version
from versioning.config import Config
from versioning.vcs import Git

config = Config(
    filepaths=[],
    defaults={
        # 'project': {'version': '1.2.3'},
        'proman': {
            'version': '1.2.3',
            'versioning': {
                'files': [
                    {
                        'filepath': 'pyproject.toml',
                        'pattern': 'version = "${version}"',
                    },
                    {
                        'filepath': 'chart/Chart.yaml',
                        'compat': 'semver',
                        'patterns': [
                            'version: "${version}"',
                            'appVersion: "${version}"',
                        ],
                    },
                ],
            },
        }
    },
)


@patch('builtins.open', new_callable=mock_open, read_data='version = "1.2.3"')
def test_create_devrelease(mock_file):
    """Test development release creation."""
    working_dir = os.path.join(os.sep, 'mock', '.git')
    controller = ReleaseController(
        repo=Git(Mock(path=working_dir, head={'name': 'mock'})),
        config=config,
        message='release: create devrelease',
    )
    assert controller.config.version == Version('1.2.3')

    controller.update_version(
        commit=False,
        # release=release,
        # tag=tag,
        # tag_name=tag_name,
        # message=message,
        # sign_tag=sign,
        # build=build,
        dry_run=True,
    )
    assert controller.config.version == Version('1.3.0.dev0')
