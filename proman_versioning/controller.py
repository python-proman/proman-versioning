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
from typing import Any

from proman_versioning.exception import PromanWorkflowException
from proman_versioning.config import Config
from proman_versioning.grammars.conventional_commits import CommitMessageParser
from proman_versioning.vcs import Git
from proman_versioning.version import Version

# from transitions import Machine

# TODO: version comparison against previous version
# has API spec been modified?
# has Python version changed?
# has requirements versions changed?

# TODO: build numbers
# git revision
# GNU build ID
# timestamp
# external (ex: CI/CD build number)


# TODO determine relation with state and git hooks
class IntegrationController(CommitMessageParser):
    """Control version releases."""

    # workflow_types = ['rolling', 'sustainment']
    # Trunk Based Development (TBD) - GitHub flow
    # Stage Based Development (SBD) - DTAP
    # Release Branching Strategy (RBS) - PEP440
    # Feature Branching Strategy (FBS) - Agile

    def __init__(
        self,
        config: Config,
        repo: Git,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Initialize commit message action object."""
        self.config = config
        # parse_current_branch = kwargs.pop('parse_current_branch', True)
        message = kwargs.pop('message', None)
        super().__init__(*args, **kwargs)

        self.vcs = repo
        if message is None:
            head = self.vcs.repo.head
            target = self.vcs.repo[head.target]
            self.parse(target.message)
        else:
            self.parse(message)

    @property
    def release(self) -> str:
        """Get the current version release state."""
        return self.config.version.state  # type: ignore

    @staticmethod
    def __get_version_regex(version: Version) -> str:
        """Get PEP-440 compliant regex for version."""
        r = '.'.join(str(x) for x in version.release)
        if version.pre:
            if version.epoch > 0:
                v = f"{version.epoch}!{r}"
            pre = version.pre[0]
            inst = version.pre[1]
            if pre == 'a' or pre == 'alpha':
                v = f"{r}[-_\\.]?(?:a|alpha)[-_\\.]?{inst or '0?'}"
            if pre == 'b' or pre == 'beta':
                v = f"{r}[-_\\.]?(?:b|beta)[-_\\.]?{inst or '0?'}"
            if pre == 'rc' or pre == 'release':
                v = f"{r}[-_\\.]?(?:rc|release)[-_\\.]?{inst or '0?'}"
            if version.dev:
                v = f"{r}[-_\\.]?dev[-_\\.]?{version.dev or '0?'}"
            return v
        if version.post:
            v = f"{r}[-_\\.]?(?:post[-_\\.]?)?{version.post}"
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
                # print(match)

    def update_configs(self, new_version: Version, **kwargs: Any) -> None:
        """Update version within config files."""
        dry_run = kwargs.pop('dry_run', False)
        stats = self.vcs.repo.diff('HEAD').stats
        if stats.files_changed == 0 or dry_run:
            if str(self.config.version) != str(new_version):
                for config in self.config.templates:
                    if 'release_only' in config and config['release_only']:
                        release = '.'.join(
                            str(x) for x in new_version.release
                        )
                        new_version = Version(release)
                    self.__update_config(
                        filepath=os.path.join(
                            self.vcs.working_dir, config['filepath']
                        ),
                        pattern=config['pattern'],
                        version=self.config.version,
                        new_version=new_version,
                        dry_run=dry_run,
                    )
                self.config.version = new_version
                if kwargs.pop('commit', True):
                    # TODO: tie scope to configs, releases or version ranges
                    scope = 'version'
                    self.vcs.commit(
                        filepaths=[
                            f['filepath']
                            for f in self.config.templates
                        ],
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
                raise PromanWorkflowException(
                    'no version update could be determined'
                )
        else:
            raise PromanWorkflowException('repository is not clean')

    def start_release(self, **kwargs: Any) -> Version:
        """Start a release."""
        new_version = deepcopy(self.config.version)
        if self.config.version.enable_devreleases and self.release == 'dev':
            new_version.start_alpha()  # type: ignore
        if self.config.version.enable_prereleases:
            if self.release == 'alpha':
                new_version.start_beta()  # type: ignore
            if self.release == 'beta':
                new_version.start_release()  # type: ignore
            if self.release == 'release':
                new_version.finish_release()  # type: ignore
        if (
            self.release == 'final'
            or (
                self.config.version.enable_postreleases
                and self.release == 'post'
            )
        ):
            new_version.start_devrelease()  # type: ignore
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
            version.bump_postrelease()
        return version

    def bump_version(self, **kwargs: Any) -> Version:
        """Update the version of the project."""
        if (
            ('type' in self.title and self.title['type'] == 'release')
            or kwargs.get('release') is True
        ):
            new_version = self.start_release(**kwargs)
            self.update_configs(new_version, **kwargs)
        else:
            new_version = deepcopy(self.config.version)
            build = kwargs.pop('build', None)

            # TODO: break, and feat should start devrelease from final or post
            # local number depends on metadata / fork / conflict existing vers
            if self.title['break'] or self.footer['breaking_change']:
                new_version.bump_major()
            elif 'type' in self.title:
                if self.title['type'] == 'feat':
                    new_version.bump_minor()
                elif self.title['type'] == 'fix':
                    new_version.bump_micro()
                elif self.title['type'] in self.config.parser.types:
                    new_version = self.__bump_release(new_version)
                else:
                    # TODO: need debug statement here instead
                    raise PromanWorkflowException(
                        'received unsupported commit type'
                    )

            # TODO: configure local version handling
            if build is not None:
                new_version.new_local(build=build)
            self.update_configs(new_version, **kwargs)
        return new_version
