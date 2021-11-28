# -*- coding: utf-8 -*-
# copyright: (c) 2021 by Jesse Johnson.
# license: MPL-2.0, see LICENSE for more details.
"""Provide configuration for versioning tools."""

import os
from dataclasses import dataclass, field, InitVar
from typing import List
# from urllib.parse import urljoin, urlparse

from compendium.config_manager import ConfigManager
from pygit2 import discover_repository

from proman_versioning.exception import PromanWorkflowException
from proman_versioning.version import Version

# TODO check VCS for paths
CURRENT_DIR = os.getcwd()
REPO_DIR = discover_repository(CURRENT_DIR)
if REPO_DIR is None:
    raise PromanWorkflowException('Unable to locate git repository.')
PROJECT_DIR = os.path.abspath(os.path.join(REPO_DIR, '..'))
CONFIG_FILES = [
    os.path.join(PROJECT_DIR, '.versioning'),
    os.path.join(PROJECT_DIR, 'pyproject.toml'),
    # TODO: add setup.cfg
]

GRAMMAR_PATH: str = os.path.join(
    os.path.dirname(__file__), 'grammars', 'conventional_commits.lark'
)
# 'proman_versioning/templates/gitmessage.j2'


# @dataclass
# class GitConfig:
#     """Manage git config."""
#
#     system_config: str = os.path.join(os.sep, 'etc', 'gitconfig')
#     global_config: str = os.path.join(os.path.expanduser('~'), '.gitconfig')


@dataclass
class Config(ConfigManager):
    """Manage settings from configuration file."""

    filepaths: InitVar[List[str]]
    writable: bool = True
    version: Version = field(init=False)

    def __post_init__(self, filepaths: List[str]) -> None:
        """Initialize settings from configuration."""
        super().__init__(filepaths=filepaths)
        super().load_configs()

        if not hasattr(self, 'version'):
            config_version = (
                self.retrieve('/proman/version')
                or self.retrieve('/tool/proman/version')
                or self.retrieve('/tool/poetry/version')
            )
            if config_version is None:
                raise PromanWorkflowException('no version found')

            self.version = Version(
                version=config_version,
                enable_devreleases=(
                    self.retrieve('/proman/versioning/enable_devreleases')
                    or self.retrieve(
                        '/tool/proman/versioning/enable_devreleases'
                    )
                ),
                enable_prereleases=(
                    self.retrieve('/proman/versioning/enable_prereleases')
                    or self.retrieve(
                        '/tool/proman/versioning/enable_prereleases'
                    )
                ),
                enable_postreleases=(
                    self.retrieve('/proman/versioning/enable_postreleases')
                    or self.retrieve(
                        '/tool/proman/versioning/enable_postreleases'
                    )
                ),
            )
