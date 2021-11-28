# -*- coding: utf-8 -*-
# copyright: (c) 2021 by Jesse Johnson.
# license: MPL-2.0, see LICENSE for more details.
"""Convenience tools to manage project versioning."""

import logging
from typing import Any, List

from pygit2 import Repository

from proman_versioning import exception
from proman_versioning.config import REPO_DIR, CONFIG_FILES, Config
from proman_versioning.controller import IntegrationController
from proman_versioning.vcs import Git
from proman_versioning.version import Version  # noqa

__author__ = 'Jesse P. Johnson'
__author_email__ = 'jpj6652@gmail.com'
__title__ = 'proman-versioning'
__description__ = 'Convenience tools to manage project versioning.'
__version__ = '0.1.1a4'
__license__ = 'MPL-2.0'
__copyright__ = 'Copyright 2021 Jesse Johnson.'

logging.getLogger(__name__).addHandler(logging.NullHandler())


def get_source_tree(config_files: List[str] = CONFIG_FILES) -> Config:
    """Get source tree from path."""
    try:
        config = Config(filepaths=config_files)
        return config
    except Exception as err:
        raise exception.PromanWorkflowException(err)


def get_release_controller(*args: Any, **kwargs: Any) -> IntegrationController:
    """Create and return a release controller."""
    repo_dir = kwargs.pop('repo_dir', REPO_DIR)
    repo = Git(Repository(repo_dir))

    config_files = kwargs.pop('config_files', CONFIG_FILES)
    cfg = get_source_tree(config_files=config_files)
    # version = get_python_version(kwargs.pop('version', cfg))

    return IntegrationController(
        version=cfg.version,
        config=cfg,
        repo=repo,
        **kwargs,
    )


__all__ = ('get_source_tree', 'get_release_controller', 'Version')
