# copyright: (c) 2021 by Jesse Johnson.
# license: LGPL-3.0, see LICENSE.md for more details.
"""Coordinate actions from commit messages."""

import difflib
import logging
import os
import re
import sys
from copy import deepcopy
from string import Template
from typing import TYPE_CHECKING, Any, Dict, Iterator

# from transitions import Machine
from versioning.exception import VersioningException
from versioning.grammars.conventional_commits import CommitMessageParser
from versioning.version import Version

if 'mdutils' not in sys.modules:
    enable_changelog = False
else:
    from versioning.changelog import Changelog

    enable_changelog = True

if TYPE_CHECKING:
    from versioning.config import Config
    from versioning.vcs import Git

# TODO: version comparison against previous version
# has API spec been modified?
# has Python version changed?
# has requirements versions changed?

# TODO: build numbers
# git revision
# GNU build ID
# timestamp
# external (ex: CI/CD build number)

log = logging.getLogger(__name__)
# TODO: need to integrate into CLI
# log.setLevel(logging.DEBUG)


# TODO determine relation with state and git hooks
class ReleaseController(CommitMessageParser):
    """Control version releases."""

    # workflow_types = ['rolling', 'sustainment']
    # Trunk Based Development (TBD) - GitLab flow
    # Stage Based Development (SBD) - DTAP
    # Release Branching Strategy (RBS) - PEP440
    # Feature Branching Strategy (FBS) - Agile

    def __init__(
        self,
        config: 'Config',
        repo: 'Git',
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Initialize commit message action object."""
        self.config = config
        # parse_current_branch = kwargs.pop('parse_current_branch', True)
        message = kwargs.pop('message', None)
        super().__init__(*args, **kwargs)

        self.vcs = repo
        self.changelog = Changelog(self.vcs.repo) if enable_changelog else None

        if message is None:
            head = self.vcs.repo.head
            target = self.vcs.repo[head.target]
            self.parse(target.message)
            log.debug('provided commit message: %r', message)
        else:
            self.parse(message)
            log.debug('found commit message: %r', message)

    @property
    def release(self) -> str:
        """Get the current version release state."""
        return self.config.version.state  # type: ignore

    def __update_config(
        self,
        config: Dict[str, Any],
        new_version: Version,
        dry_run: bool = False,
    ) -> Iterator[str]:
        """Update target file with new version."""
        version = deepcopy(self.config.version)

        # handle compatiblity with semver
        if 'compat' in config:
            version.compat = config['compat']
            new_version.compat = config['compat']

        filepath = os.path.join(self.vcs.working_dir, config['filepath'])

        # TODO: handle when file does not exist
        with open(filepath, 'r+', encoding='utf-8') as file:
            file_contents = file.read()

            for pattern in (
                config['patterns']
                if 'patterns' in config
                else [config['pattern']]
            ):
                template = Template(pattern).substitute(version=version.query)
                match = re.compile(
                    # XXX: escape not compiling correctly
                    template,  # re.escape(template),
                    flags=0,
                )
                log.debug('applying pattern for source version %s', match)

                # substitute the expression in file
                file_update = match.sub(
                    Template(pattern).substitute(version=str(new_version)),
                    file_contents,
                )

            deltas = difflib.unified_diff(
                file_contents.splitlines(),
                file_update.splitlines(),
                fromfile=filepath,
            )

            if not dry_run:
                # check version file update is applied
                if not list(deltas):
                    raise VersioningException(
                        f"version update was not applied to {filepath}"
                    )
                # save the file
                try:
                    file.seek(0)
                    file.truncate()
                    file.write(file_update)
                    log.info('writting file at: %r', filepath)
                except OSError as err:
                    print(err, file=sys.stderr)
            else:
                log.info(
                    'view version update instead of file write at: %r',
                    filepath,
                )
                # diff the file changes
                for x in deltas:
                    print(x, file=sys.stdout)
            return deltas

    def _update_configs(self, new_version: Version, **kwargs: Any) -> None:
        """Update version within config files."""
        dry_run = kwargs.pop('dry_run', False)
        if self.vcs.repo.diff('HEAD').stats.files_changed == 0 or dry_run:
            if self.config.version != new_version:
                # TODO: create tarfile here
                for config in self.config.templates:
                    # NOTE: need conditional here to switch update or patch
                    self.__update_config(
                        config=config,
                        new_version=new_version,
                        dry_run=dry_run,
                    )
                    # TODO: add diffs to tarfile

                self.config.version = new_version
                make_commit = kwargs.pop('commit', True)
                make_tag = kwargs.pop('tag', False)
                if make_commit or make_tag:
                    # TODO: tie scope to configs, releases or version ranges
                    scope = 'version'
                    self.vcs.commit(
                        filepaths=[
                            f['filepath'] for f in self.config.templates
                        ],
                        message=(
                            f"ci({scope}): apply {str(new_version)} updates"
                        ),
                        dry_run=dry_run,
                    )
                    log.info('commiting version changes: %s', str(new_version))

                    if make_tag:
                        self.vcs.tag(
                            name=str(new_version),
                            ref='HEAD',
                            message=None,
                            dry_run=dry_run,
                        )
                        log.info('applying tag: %s', str(new_version))
            else:
                raise VersioningException('version could not be determined')
        else:
            raise VersioningException('repository is not clean')

    def update_version(self, **kwargs: Any) -> Version:
        """Update the version of the project."""
        new_version = deepcopy(self.config.version)
        if self.changelog:
            self.changelog.generate_changelog()
        if (
            'type' in self.title and self.title['type'] == 'release'
        ) or kwargs.get('release') is True:
            new_version.start_release(segment='minor')  # type: ignore
        else:
            build = kwargs.pop('build', None)

            # TODO: break and feat should start devrelease from final or post
            # local number depends on metadata / fork / conflict existing
            # versions
            if self.title['break'] or self.footer['breaking_change']:
                new_version.bump_major()  # type: ignore
            elif 'type' in self.title:
                if self.title['type'] == 'feat':
                    new_version.bump_minor()  # type: ignore
                elif self.title['type'] == 'fix':
                    new_version.bump_micro()  # type: ignore
                elif self.title['type'] in self.config.parser.types:
                    # new_version = self.__bump_release(new_version)
                    new_version.bump_release()  # type: ignore
                else:
                    # TODO: need debug statement here instead
                    raise VersioningException(
                        'received unsupported commit type'
                    )

            # TODO: configure local version handling
            if build is not None:
                new_version._new_local(local=build)
        self._update_configs(new_version, **kwargs)
        return new_version

    def push_changes(self, **kwargs: Any) -> None:
        """Push changes to repository."""
        branch = kwargs.pop('branch')
        remote = kwargs.pop('remote')
        remote_branch = kwargs.pop('remote_branch')
        remote_url = kwargs.pop('remote_url')
        username = kwargs.pop('username')
        password = kwargs.pop('password')

        if remote_url is not None:
            # TODO: feels like it would be smarter to encapsulate
            # credentials with a remote.
            self.vcs.add_remote(
                remote,
                remote_url,
                # username=username,
                # password=password,
            )
        self.vcs.push(
            branch=branch or self.vcs.branch,
            remote=remote or 'origin',
            remote_branch=remote_branch,
            username=username,
            password=password,
        )
