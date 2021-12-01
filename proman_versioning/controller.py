# -*- coding: utf-8 -*-
# copyright: (c) 2021 by Jesse Johnson.
# license: MPL-2.0, see LICENSE for more details.
"""Parse Git commit messages."""

# import logging
import os
import re
import sys
from copy import deepcopy
from string import Template
from typing import Any, Dict, List

from proman_versioning.exception import PromanWorkflowException
from proman_versioning.config import Config
from proman_versioning.grammars.conventional_commits import CommitMessageParser
from proman_versioning.vcs import Git
from proman_versioning.version import Version

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
        version: Version,
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

    @property
    def filepaths(self) -> List[Dict[str, Any]]:
        """List templated filepaths."""
        filepaths = (
            self.config.retrieve('/proman/versioning/files')
            or self.config.retrieve('/tool/proman/versioning/files')
        )
        if not filepaths:
            raise PromanWorkflowException('no files for templating foundd')
        return filepaths

    @staticmethod
    def __get_version_regex(version: Version) -> str:
        """Get PEP-440 compliant regex for version."""
        v = '.'.join([str(x) for x in version.release])
        if version.pre:
            if version.epoch > 0:
                v = f"{version.epoch}!{v}"
            pre = version.pre[0]
            if pre == 'a' or pre == 'alpha':
                v = f"{v}[-_\\.]?(?:a|alpha)[-_\\.]?{version.pre[1] or ''}"
            if pre == 'b' or pre == 'beta':
                v = f"{v}[-_\\.]?(?:b|beta)[-_\\.]?{version.pre[1] or ''}"
            if pre == 'rc' or pre == 'release':
                v = f"{v}[-_\\.]?(?:rc|release)[-_\\.]?{version.pre[1] or ''}"
            if version.dev:
                v = f"{v}{version.dev[0]}{version.dev[1]}"
            return v
        if version.post:
            v = f"{v}[-_\\.]?(?:post[-_\\.]?)?{version.post[1]}"
            return v
        else:
            return str(version)

    @staticmethod
    def __update_config(
        filepath: str,
        pattern: str,
        version: Version,
        new_version: Version,
        dry_run: bool = False,
    ) -> None:
        """Update config file with new file."""
        # TODO: handle when file does not exist
        with open(filepath, 'r+') as f:
            file_contents = f.read()

            # prepare source expression match pattern
            version_str = IntegrationController.__get_version_regex(
                version=version
            )
            template = Template(pattern).substitute(version=version_str)
            match = re.compile(
                # XXX: escape not compiling correctly
                template,  # re.escape(template),
                flags=0,
            )

            # substitute the expression in file
            file_contents = match.sub(
                Template(pattern).substitute(version=str(new_version)),
                file_contents,
            )

            if not dry_run:
                # save the file
                try:
                    f.seek(0)
                    f.truncate()
                    f.write(file_contents)
                except Exception as err:
                    print(err, file=sys.stderr)
            else:
                # print the file changes
                print(file_contents, file=sys.stdout)

    def update_configs(self, new_version: Version, **kwargs: Any) -> None:
        """Update version within config files."""
        dry_run = kwargs.pop('dry_run', False)
        stats = self.vcs.repo.diff('HEAD').stats
        if stats.files_changed == 0 or dry_run:
            if str(self.version) != str(new_version):
                for filepath in self.filepaths:
                    if 'release_only' in filepath and filepath['release_only']:
                        release = '.'.join(
                            [str(x) for x in new_version.release]
                        )
                        new_version = Version(release)
                    self.__update_config(
                        filepath=os.path.join(
                            self.vcs.working_dir, filepath['filepath']
                        ),
                        pattern=filepath['pattern'],
                        version=self.version,
                        new_version=new_version,
                        dry_run=dry_run,
                    )
                self.version = new_version
                if kwargs.pop('commit', True):
                    # TODO: tie scope to configs, releases or version ranges
                    scope = 'version'
                    self.vcs.commit(
                        filepaths=[f['filepath'] for f in self.filepaths],
                        message=(f"ci({scope}): apply {new_version} updates"),
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
                raise PromanWorkflowException('no new version available')
        else:
            raise PromanWorkflowException('git repository is not clean')

    def start_release(self, kind: str = 'dev', **kwargs: Any) -> Version:
        """Start a release."""
        new_version = deepcopy(self.version)
        if kind == 'dev':
            new_version.start_devrelease()  # type: ignore
        elif kind == 'pre':
            new_version.start_prerelease()  # type: ignore
        self.update_configs(new_version, **kwargs)
        return new_version

    def finish_release(self, **kwargs: Any) -> Version:
        """Finish a release."""
        new_version = deepcopy(self.version)
        new_version.finish_release()  # type: ignore
        self.update_configs(new_version, **kwargs)
        return new_version

    @staticmethod
    def __bump_release(version: Version) -> Version:
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

    def bump_version(self, **kwargs: Any) -> Version:
        """Update the version of the project."""
        new_version = deepcopy(self.version)
        build = kwargs.pop('build', None)

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
        # TODO: configure local version handling
        if build is not None:
            new_version = Version(f"{new_version}+{build}")

        self.update_configs(new_version, **kwargs)
        return new_version
