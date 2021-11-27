# -*- coding: utf-8 -*-
# copyright: (c) 2021 by Jesse Johnson.
# license: MPL-2.0, see LICENSE for more details.
"""Convenience tools to manage project versioning."""

import logging
import os
from typing import Any

from pygit2 import Repository

from proman_versioning import exception
from proman_versioning.config import BASE_DIR, CONFIG_PATH, Config
from proman_versioning.controller import IntegrationController
from proman_versioning.vcs import Git
from proman_versioning.version import Version  # noqa

__author__ = 'Jesse P. Johnson'
__author_email__ = 'jpj6652@gmail.com'
__title__ = 'proman-versioning'
__description__ = 'Convenience tools to manage project versioning.'
__version__ = '0.1.1a3'
__license__ = 'MPL-2.0'
__copyright__ = 'Copyright 2021 Jesse Johnson.'

logging.getLogger(__name__).addHandler(logging.NullHandler())


def get_source_tree(config_path: str = CONFIG_PATH) -> Config:
    """Get source tree from path."""
    if os.path.isfile(config_path):
        return Config(filepath=config_path)
    raise exception.PromanWorkflowException('no configuration found')


def get_release_controller(*args: Any, **kwargs: Any) -> IntegrationController:
    """Create and return a release controller."""
    base_dir = kwargs.get('base_dir', BASE_DIR)
    repo = Git(Repository(base_dir))

    config_path = kwargs.get('config_path', CONFIG_PATH)
    cfg = get_source_tree(config_path=config_path)
    # version = get_python_version(kwargs.pop('version', cfg))

    return IntegrationController(
        version=cfg.version,
        config=cfg,
        repo=repo,
        **kwargs,
    )


__all__ = ('get_source_tree', 'get_release_controller', 'Version')
