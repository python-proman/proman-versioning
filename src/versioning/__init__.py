# copyright: (c) 2021 by Jesse Johnson.
# license: LGPL-3.0, see LICENSE.md for more details.
"""Initialize versioning instances."""

import logging
from typing import Any

from pygit2 import Repository

from versioning.config import CONFIG_FILES, REPO_DIR, Config
from versioning.controller import ReleaseController
from versioning.exception import VersioningException
from versioning.vcs import Git
from versioning.version import Version  # noqa

__author__ = 'Jesse P. Johnson'
__author_email__ = 'jpj6652@gmail.com'
__title__ = 'proman-versioning'
__description__ = 'Workflows to manage project versioning.'
__version__ = '0.7.1a0'
__license__ = 'LGPL-3.0'
__copyright__ = 'Copyright 2021 Jesse Johnson.'
__all__ = (
    'ReleaseController',
    'get_release_controller',
    'Version',
)

logging.getLogger(__name__).addHandler(logging.NullHandler())


def get_release_controller(**kwargs: Any) -> ReleaseController:
    """Create and return a release controller."""
    try:
        repo_dir = kwargs.pop('repo_dir', REPO_DIR)
        repo = Git(Repository(repo_dir))

        config_files = kwargs.pop('config_files', CONFIG_FILES)
        config = Config(filepaths=config_files)

        return ReleaseController(config=config, repo=repo, **kwargs)
    except Exception as err:
        raise VersioningException(err) from err
