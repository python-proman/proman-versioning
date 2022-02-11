# copyright: (c) 2021 by Jesse Johnson.
# license: LGPL-3.0, see LICENSE.md for more details.
"""Initialize versioning instances."""

import logging
from typing import Any, List

from pygit2 import Repository

from versioning.config import CONFIG_FILES, REPO_DIR, Config
from versioning.controller import IntegrationController
from versioning.exception import PromanVersioningException
from versioning.vcs import Git
from versioning.version import Version  # noqa

__author__ = 'Jesse P. Johnson'
__author_email__ = 'jpj6652@gmail.com'
__title__ = 'proman-versioning'
__description__ = 'Workflows to manage project versioning.'
__version__ = '0.4.3a2'
__license__ = 'LGPL-3.0'
__copyright__ = 'Copyright 2021 Jesse Johnson.'
__all__ = (
    'IntegrationController',
    'get_source_tree',
    'get_release_controller',
    'Version'
)

logging.getLogger(__name__).addHandler(logging.NullHandler())


def get_source_tree(config_files: List[str] = CONFIG_FILES) -> Config:
    """Get source tree from path."""
    try:
        config = Config(filepaths=config_files)
        return config
    except Exception as err:
        raise PromanVersioningException(err)


def get_release_controller(*args: Any, **kwargs: Any) -> IntegrationController:
    """Create and return a release controller."""
    repo_dir = kwargs.pop('repo_dir', REPO_DIR)
    repo = Git(Repository(repo_dir))

    config_files = kwargs.pop('config_files', CONFIG_FILES)
    cfg = get_source_tree(config_files=config_files)

    return IntegrationController(config=cfg, repo=repo, **kwargs)
