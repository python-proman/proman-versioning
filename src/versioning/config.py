# copyright: (c) 2021 by Jesse Johnson.
# license: LGPL-3.0, see LICENSE.md for more details.
"""Provide configuration for versioning tools."""

import os
from dataclasses import InitVar, asdict, dataclass, field
from typing import Any, Dict, List

from compendium.config_manager import ConfigManager
from pygit2 import discover_repository

from versioning.exception import VersioningException
from versioning.version import Version

# from urllib.parse import urljoin, urlparse

# TODO check VCS for paths
CURRENT_DIR = os.getcwd()
REPO_DIR = (
    f"{CURRENT_DIR}/.git"
    if os.path.exists(f"{CURRENT_DIR}/.git")
    else discover_repository(CURRENT_DIR)
)
if REPO_DIR is None:
    raise VersioningException('Unable to locate git repository.')
PROJECT_DIR = os.path.abspath(os.path.join(REPO_DIR, os.pardir))
CONFIG_FILES = [
    os.path.join(PROJECT_DIR, '.version'),
    os.path.join(PROJECT_DIR, '.versioning'),
    os.path.join(PROJECT_DIR, 'pyproject.toml'),
    # TODO: add setup.cfg
]

GRAMMAR_PATH: str = os.path.join(
    os.path.dirname(__file__), 'grammars', 'conventional_commits.lark'
)
# 'versioning/templates/gitmessage.j2'


# @dataclass
# class GitConfig:
#     """Manage git config."""
#
#     system_config: str = os.path.join(os.sep, 'etc', 'gitconfig')
#     global_config: str = os.path.join(os.path.expanduser('~'), '.gitconfig')


@dataclass
class ParserConfig:
    """Configure parser operation."""

    config: InitVar[Dict[str, Any]] = None
    types: List[str] = field(default_factory=list)
    scopes: List[str] = field(default_factory=list)

    def __post_init__(self, config: Dict[str, Any]) -> None:
        """Configure VCS message parsing."""
        # thinking builtin types might not need to be here
        # if (
        #     self.types == []
        #     and 'types' in config
        #     and config['types'] != []
        # ):
        #     self.types = config['types']
        #     if 'feat' not in self.types:
        #         self.types.insert(0, 'feat')
        #     if 'fix' not in self.types:
        #         self.types.insert(1, 'fix')
        #     if 'release' not in self.types:
        #         self.types.insert(2, 'release')
        # else:
        #     self.types = ['feat', 'fix', 'release']

        if (
            self.types == []
            and config is not None
            and 'types' in config
            and config['types'] != []
        ):
            self.types = config['types']

        if (
            self.scopes == []
            and config is not None
            and 'scopes' in config
            and config['scopes'] != []
        ):
            self.scopes = config['scopes']


@dataclass
class ReleaseConfig:
    """Configure release operation."""

    config: InitVar[Dict[str, Any]] = None
    compat: str = 'pep440'
    enable_prereleases: bool = True
    enable_postreleases: bool = True
    enable_devreleases: bool = True

    def __post_init__(self, config: Dict[str, Any]) -> None:
        """Load configuration for release operation."""
        if 'compat' in config:
            self.compat = config['compat']

        if 'enable_prereleases' in config:
            self.enable_prereleases = config['enable_prereleases']
        elif self.compat == 'numeric':
            self.enable_prereleases = False

        if 'enable_postreleases' in config:
            self.enable_postreleases = config['enable_postreleases']
        elif self.compat == 'numeric':
            self.enable_postreleases = False

        if 'enable_devreleases' in config:
            self.enable_devreleases = config['enable_devreleases']
        elif self.compat == 'semver':
            self.enable_devreleases = False


# @dataclass
# class TemplateConfig:
#     """Configure template layout."""
#
#     filepath: str
#     pattern: str


@dataclass
class Config(ConfigManager):
    """Manage settings from configuration file."""

    filepaths: InitVar[List[str]]
    defaults: InitVar[Dict[str, Any]] = field(default={})
    templates: List[Dict[str, Any]] = field(default_factory=list)
    parser: ParserConfig = field(init=False)
    release: ReleaseConfig = field(init=False)
    version: Version = field(init=False)

    def __post_init__(
        self, filepaths: List[str], defaults: Dict[str, Any]
    ) -> None:
        """Initialize settings from configuration."""
        super().__init__(filepaths=filepaths, separator='.', defaults=defaults)

        # load configuration from paths in order or precedence
        config = self.lookup('versioning', 'tool.proman.versioning') or {}
        if 'files' in config and config['files'] != []:
            self.templates += config['files']

        self.templates += [
            {
                'filepath': os.path.basename(x),
                'pattern': "version = \"${version}\"",
            }
            for x in filepaths
            if os.path.exists(x)
            and os.path.basename(x)
            not in [x['filepath'] for x in self.templates]
        ]
        # os.path.relpath(CONFIG_FILES[0], start=PROJECT_DIR),

        if 'types' not in config:
            angular_convention = [
                'build',
                'ci',
                'docs',
                'perf',
                'refactor',
                'style',
                'test',
            ]
            config['types'] = angular_convention
        self.parser = ParserConfig(config=config)

        config_version = self.lookup(
            'version',
            'project.version',
            'proman.version',
            'tool.proman.version',
        )
        # if config_version is None:
        #     raise VersioningException('no version found in filepaths')

        # TODO: use different version based on config
        self.version = Version(
            version=str(config_version),
            **asdict(ReleaseConfig(config=config)),
        )
