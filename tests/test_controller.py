# -*- coding: utf-8 -*-
# type: ignore
"""Test git hooks pipeline."""

import os
from unittest.mock import patch, Mock, mock_open

from proman_versioning import IntegrationController, Version
from proman_versioning.config import Config
from proman_versioning.vcs import Git

config = Config(
    filepaths=['pyproject.toml'],
    defaults={
        'proman': {
            'version': '1.2.3',
            'versioning': {
                'files': [
                    {
                        'filepath': 'pyproject.toml',
                        'pattern': 'version = "${version}"'
                    },
                ],
            },
        }
    }
)


@patch(
    'builtins.open',
    new_callable=mock_open,
    read_data='version = "1.2.3"'
)
def test_create_devrelease(mock_file):
    working_dir = os.path.join(os.sep, 'mock', '.git')
    controller = IntegrationController(
        repo=Git(Mock(path=working_dir, head={'name': 'mock'})),
        config=config,
        message='release: create devrelease'
    )
    assert controller.config.version == Version('1.2.3')

    controller.bump_version(
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
