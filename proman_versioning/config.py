# -*- coding: utf-8 -*-
# copyright: (c) 2020 by Jesse Johnson.
# license: MPL-2.0, see LICENSE for more details.
"""Provide configuration for versioning tools."""

import os
from dataclasses import dataclass, field
from typing import Optional, Tuple
from urllib.parse import urljoin, urlparse

from compendium.loader import ConfigFile
from pygit2 import discover_repository

from proman_versioning import exception
from proman_versioning.version import PythonVersion

INDEX_URL = urlparse('https://pypi.org')

# TODO check VCS for paths
CURRENT_DIR = os.getcwd()
BASE_DIR = discover_repository(CURRENT_DIR)
WORKING_DIR = os.path.abspath(os.path.join(BASE_DIR, '..'))  
FILENAMES = ['pyproject.toml', 'setup.self']

GRAMMAR_PATH: str = os.path.join(
    os.path.dirname(__file__), 'grammars', 'conventional_commits.lark'
)
# 'proman_versioning/templates/gitmessage.j2'


@dataclass
class GitConfig:
    """Manage git config."""

    system_config: str = os.path.join(os.sep, 'etc', 'gitconfig')
    global_config: str = os.path.join(os.path.expanduser('~'), '.gitconfig')


@dataclass
class Config(ConfigFile):
    """Manage settings from configuration file."""

    filepath: str
    index_url: str = urljoin(INDEX_URL.geturl(), 'simple')
    python_versions: tuple = ()
    digest_algorithm: str = 'sha256'
    include_prereleases: bool = False
    lookup_memory: Optional[str] = None
    writable: bool = True
    version: PythonVersion = field(init=False)

    def __post_init__(self) -> None:
        """Initialize settings from configuration."""
        super().__init__(self.filepath)
        if os.path.isfile(self.filepath):
            self.load()

        if not hasattr(self, 'version'):
            config_version = (
                self.retrieve('/tool/proman/versioning/version')
                or self.retrieve('/tool/proman/version')
                or self.retrieve('/tool/poetry/version')
                or self.retrieve('/metadata/version')
            )
            if config_version is None:
                raise exception.PromanWorkflowException('no version found')

            self.version = PythonVersion(
                version=config_version,
                enable_devreleases=self.retrieve(
                    '/tool/proman/versioning/enable_devreleases', False
                ),
                enable_prereleases=self.retrieve(
                    '/tool/proman/versioning/enable_prereleases', False
                ),
                enable_postreleases=self.retrieve(
                    '/tool/proman/versioning/enable_postreleases', False
                ),
            )
