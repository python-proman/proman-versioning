# -*- coding: utf-8 -*-
# copyright: (c) 2021 by Jesse Johnson.
# license: MPL-2.0, see LICENSE for more details.
"""Convenience tools to manage project versioning."""

import logging
import os
from typing import Any, List, Union

from pygit2 import Repository

from proman_versioning import exception
from proman_versioning.config import BASE_DIR, FILENAMES, WORKING_DIR, Config
from proman_versioning.controller import IntegrationController
from proman_versioning.vcs import Git
from proman_versioning.version import PythonVersion

__author__ = 'Jesse P. Johnson'
__author_email__ = 'jpj6652@gmail.com'
__title__ = 'proman-versioning'
__description__ = 'Convenience tools to manage project versioning.'
__version__ = '0.1.1a2'
__license__ = 'MPL-2.0'
__copyright__ = 'Copyright 2021 Jesse Johnson.'

logging.getLogger(__name__).addHandler(logging.NullHandler())


def get_source_tree(
    working_dir: str = WORKING_DIR, filenames: List[str] = FILENAMES
) -> Config:
    """Get source tree from path."""
    for filename in filenames:
        filepath = os.path.join(working_dir, filename)
        if os.path.isfile(filepath):
            return Config(filepath=filepath)
    raise exception.PromanWorkflowException('no configuration found')


def get_release_controller(*args: Any, **kwargs: Any) -> IntegrationController:
    """Create and return a release controller."""
    base_dir = kwargs.get('base_dir', BASE_DIR)
    repo = Git(Repository(base_dir))

    working_dir = kwargs.get('working_dir', WORKING_DIR)
    filenames = kwargs.get('filenames', FILENAMES)
    cfg = get_source_tree(working_dir=working_dir, filenames=filenames)
    # version = get_python_version(kwargs.pop('version', cfg))

    return IntegrationController(
        version=cfg.version,
        config=cfg,
        repo=repo,
        **kwargs,
    )


__all__ = [
    'get_source_tree',
    'get_release_controller',
]
