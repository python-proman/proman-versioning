# -*- coding: utf-8 -*-
# copyright: (c) 2020 by Jesse Johnson.
# license: MPL-2.0, see LICENSE for more details.
"""Parse Git commit messages."""

# import logging
import os
import re
import sys
from copy import deepcopy
from string import Template
from typing import Any

from proman_versioning import exception
from proman_versioning.config import Config
from proman_versioning.grammars.conventional_commits import CommitMessageParser
from proman_versioning.vcs import Git
from proman_versioning.version import PythonVersion

# from packaging.version import Version
# from transitions import Machine

# TODO: version comparison against previous version
# has API spec been modified?
# has Python version changed?
# has requirements versions changed?


# TODO determine relation with state and git hooks
class IntegrationController(CommitMessageParser):
    """Control version releases."""

    # kinds = ['rolling', 'sustainment']
    # Trunk Based Development (TBD) - GitHub flow
    # Stage Based Development (SBD) - use of DTAP
    # Release Branching Strategy (RBS) - PEP440
    # Feature Branching Strategy (FBS) - Agile

    def __init__(
        self,
        version: PythonVersion,
        config: Config,
        repo: Git,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Initialize commit message action object."""
        self.version = version
        self.config = config
        parse_current_repo = kwargs.pop('parse_current_repo', True)
        super().__init__(*args, **kwargs)

        self.vcs = repo
        if parse_current_repo:
            head = self.vcs.repo.head
            target = self.vcs.repo[head.target]
            self.parse(target.message)

    @staticmethod
    def __update_config(
        filepath: str,
        version: str,
        new_version: str,
        dry_run: bool = False,
    ) -> None:
        """Update config file with new file."""
        # TODO: if file does not exist
        # XXX: template does not handle various pep440 formats
        with open(filepath, 'r+') as f:
            file_contents = f.read()
            pattern = re.compile(re.escape(version), flags=0)
            file_contents = pattern.sub(new_version, file_contents)
            if not dry_run:
                try:
                    f.seek(0)
                    f.truncate()
                    f.write(file_contents)
                except Exception as err:
                    print(err, file=sys.stderr)
            else:
                print(file_contents, file=sys.stdout)

    def update_configs(
        self, new_version: PythonVersion, **kwargs: Any
    ) -> None:
        """Update version within config files."""
        dry_run = kwargs.pop('dry_run', False)
        stats = self.vcs.repo.diff('HEAD').stats
        if stats.files_changed == 0 or dry_run:
            if str(self.version) != str(new_version):
                filepaths = (
                    self.config['tool']['proman']['versioning']['files']
                )
                for filepath in filepaths:
                    self.__update_config(
                        filepath=os.path.join(
                            self.vcs.working_dir, filepath['filepath']
                        ),
                        version=(
                            Template(filepath['pattern']).substitute(
                                version=str(self.version)
                            )
                        ),
                        new_version=(
                            Template(filepath['pattern']).substitute(
                                version=str(new_version)
                            )
                        ),
                        dry_run=dry_run,
                    )
                self.version = new_version
                if kwargs.pop('commit', True):
                    self.vcs.commit(
                        filepaths=[f['filepath'] for f in filepaths],
                        message=(f"ci(version): apply {new_version} updates"),
                        dry_run=dry_run,
                    )
                if kwargs.get('tag', False):
                    self.vcs.tag(
                        name=str(new_version),
                        ref='HEAD',
                        message=None,
                        dry_run=dry_run,
                    )
            else:
                raise exception.PromanWorkflowException(
                    'no new version available'
                )
        else:
            raise exception.PromanWorkflowException(
                'git repository is not clean'
            )

    def start_release(self, kind: str = 'dev', **kwargs: Any) -> str:
        """Start a release."""
        new_version = deepcopy(self.version)
        if kind == 'dev':
            new_version.start_devrelease()  # type: ignore
        elif kind == 'pre':
            new_version.start_prerelease()  # type: ignore
        self.update_configs(new_version, **kwargs)
        return str(new_version)

    def finish_release(self, **kwargs: Any) -> str:
        """Finish a release."""
        new_version = deepcopy(self.version)
        new_version.finish_release()  # type: ignore
        self.update_configs(new_version, **kwargs)
        return str(new_version)

    @staticmethod
    def __bump_release(version: PythonVersion) -> PythonVersion:
        """Update release number."""
        if version.is_devrelease:
            version.bump_devrelease()
        elif version.is_prerelease:
            version.bump_prerelease()
        elif version.is_postrelease:
            version.bump_postrelease()
        elif version.enable_postreleases:
            version.start_postrelease()  # type: ignore
        return version

    def bump_version(self, **kwargs: Any) -> str:
        """Update the version of the project."""
        new_version = deepcopy(self.version)

        # local number depends on metadata / fork / conflict existing vers
        if self.title['break'] or self.footer['breaking_change']:
            new_version.bump_major()
        elif 'type' in self.title:
            if self.title['type'] == 'feat':
                new_version.bump_minor()
            elif self.title['type'] == 'fix':
                new_version.bump_micro()

            # update release instance
            elif self.title['type'] == 'build':
                new_version = self.__bump_release(new_version)
            elif self.title['type'] == 'ci':
                new_version = self.__bump_release(new_version)
            elif self.title['type'] == 'docs':
                new_version = self.__bump_release(new_version)
            elif self.title['type'] == 'perf':
                new_version = self.__bump_release(new_version)
            elif self.title['type'] == 'refactor':
                new_version = self.__bump_release(new_version)
            elif self.title['type'] == 'style':
                new_version = self.__bump_release(new_version)
            elif self.title['type'] == 'test':
                new_version = self.__bump_release(new_version)
            elif self.title['type'] == 'chore':
                new_version = self.__bump_release(new_version)

        self.update_configs(new_version, **kwargs)
        return str(new_version)
