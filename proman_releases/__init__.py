# -*- coding: utf-8 -*-
# copyright: (c) 2021 by Jesse Johnson.
# license: Apache 2.0, see LICENSE for more details.
'''Convenience tools to manage Git projects with Python.'''

import logging
import os
from typing import Any, List, Union

from git import Repo

from proman_releases import config, exception
from proman_releases.config import Config
from proman_releases.controller import IntegrationController
from proman_releases.grammars.conventional_commits import CommitMessageParser
from proman_releases.vcs import Git
from proman_releases.version import PythonVersion

logging.getLogger(__name__).addHandler(logging.NullHandler())

__author__ = 'Jesse P. Johnson'
__author_email__ = 'jpj6652@gmail.com'
__title__ = 'proman-releases'
__description__ = 'Convenience module to manage VCS tools with Python.'
__version__ = '0.1.0'
__license__ = 'Apache-2.0'
__copyright__ = 'Copyright 2021 Jesse Johnson.'


def get_repo(path: str = os.getcwd()) -> Git:
    '''Load the repository object.'''
    return Git(Repo(os.path.join(path)))


def get_source_tree(
    basepath: str = os.getcwd(), filenames: List[str] = config.filenames
) -> Config:
    '''Get source tree from path.'''
    for filename in filenames:
        filepath = os.path.join(basepath, filename)
        if os.path.isfile(filepath):
            return Config(filepath=filepath)
    raise exception.PromanWorkflowException('no configuration found')


def get_python_version(cfg: Union[Config, str]) -> PythonVersion:
    '''Get python version from configurations.'''
    if isinstance(cfg, Config):
        if (
            cfg['tool']['proman']['release']
            and 'version' in cfg['tool']['proman']['release']
        ):
            v = cfg.retrieve('/tool/proman/release/version')
        elif (
            cfg['tool']['proman']
            and 'version' in cfg['tool']['proman']
        ):
            v = cfg.retrieve('/tool/proman/version')
        elif 'version' in cfg['tool']['poetry']:
            v = cfg.retrieve('/tool/poetry/version')
        elif cfg.retrieve('/metadata'):
            v = cfg.retrieve('/metadata/version')
        else:
            raise exception.PromanWorkflowException('no version found')
        version = PythonVersion(
            version=v,
            enable_devreleases=cfg.retrieve(
                '/tool/proman/release/enable_devreleases', False
            ),
            enable_prereleases=cfg.retrieve(
                '/tool/proman/release/enable_prereleases', False
            ),
            enable_postreleases=cfg.retrieve(
                '/tool/proman/release/enable_postreleases', False
            ),
        )
    else:
        version = PythonVersion(cfg)
    return version


def get_release_controller(*args: Any, **kwargs: Any) -> IntegrationController:
    '''Create and return a release controller.'''
    basepath = kwargs.get('basepath', os.getcwd())
    filenames = kwargs.get('filenames', config.filenames)
    cfg = get_source_tree(basepath=basepath, filenames=filenames)
    version = get_python_version(kwargs.pop('version', cfg))
    return IntegrationController(
        version=version,
        config=cfg,
        repo=get_repo(basepath),
        **kwargs,
    )


repo = get_repo()
source_tree = get_source_tree()
parser = CommitMessageParser()

__all__ = [
    'get_repo',
    'get_source_tree',
    'get_release_controller',
    'parser',
    'repo',
    'source_tree',
]
