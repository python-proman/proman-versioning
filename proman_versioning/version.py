# -*- coding: utf-8 -*-
# copyright: (c) 2021 by Jesse Johnson.
# license: MPL-2.0, see LICENSE for more details.
"""Manage version numbers."""

# import logging
from typing import Any, List, Optional, Tuple

from packaging.version import (
    Version as PackageVersion, _cmpkey, _parse_local_version, _Version
)
from transitions import Machine


class Version(PackageVersion):
    """Provide PEP440 compliant versioning."""

    def __init__(self, version: str, **kwargs: Any) -> None:
        """Initialize version object."""
        # self.kind = kwargs.pop('version_system', 'semver')
        super().__init__(version=version)

        # TODO: transitions here should be populated by VCS workflow
        self.enable_devreleases = kwargs.get('enable_devreleases', True)
        self.enable_prereleases = kwargs.get('enable_prereleases', True)
        self.enable_postreleases = kwargs.get('enable_postreleases', True)

        self.machine = Machine(
            self, states=self.states, initial=self.get_state()
        )

        self.machine.add_transition(
            trigger='start_local',
            source=['final', 'release', 'development', 'post'],
            dest='local',
            before='new_local',
        )

        # dev-releases
        self.machine.add_transition(
            trigger='start_devrelease',
            source=['final', 'release', 'post'],
            dest='development',
            before='new_devrelease',
            conditions=['devreleases_enabled'],
        )

        # pre-release
        self.machine.add_transition(
            trigger='start_prerelease',
            source=['final', 'development', 'post'],
            dest='alpha',
            before='new_prerelease',
            conditions=['prereleases_enabled'],
        )
        self.machine.add_transition(
            trigger='start_prerelease',
            source='alpha',
            dest='beta',
            before='new_prerelease',
            conditions=['prereleases_enabled'],
        )
        self.machine.add_transition(
            trigger='start_prerelease',
            source='beta',
            dest='release',
            before='new_prerelease',
            conditions=['prereleases_enabled'],
        )

        # final release
        self.machine.add_transition(
            trigger='finish_release',
            source=['local', 'development', 'release'],
            dest='final',
            before='finalize_release',
        )

        # post-releases
        self.machine.add_transition(
            trigger='start_postrelease',
            source='final',
            dest='post',
            before='new_postrelease',
            conditions=['postreleases_enabled'],
        )

    @property
    def states(self) -> List[str]:
        """List all states."""
        states = ['local', 'final']
        if self.enable_devreleases:
            states += ['development']
        if self.enable_prereleases:
            states += ['alpha', 'beta', 'release']
        if self.enable_postreleases:
            states += ['post']
        return states

    @property
    def devreleases_enabled(self) -> bool:
        """Check if devreleases are enabled."""
        return self.enable_devreleases

    @property
    def prereleases_enabled(self) -> bool:
        """Check if prereleases are enabled."""
        return self.enable_prereleases

    @property
    def postreleases_enabled(self) -> bool:
        """Check if postreleases are enabled."""
        return self.enable_postreleases

    def get_prerelease(self) -> Optional[str]:
        """Get current prerelease state."""
        if self.pre:
            if self.pre[0] == 'a':
                return 'alpha'
            elif self.pre[0] == 'b':
                return 'beta'
            elif self.pre[0] == 'rc':
                return 'release'
        return None

    def get_state(self) -> str:
        """Get the current state of package release."""
        if self.is_devrelease:
            state = 'development'
        elif self.is_prerelease:
            state = 'prerelease'
        elif self.is_postrelease:
            state = 'post'
        else:
            state = 'final'
        return state

    def __update_version(
        self,
        epoch: Optional[int] = None,
        release: Optional[Tuple[Any, ...]] = None,
        pre: Optional[Tuple[str, int]] = None,
        post: Optional[Tuple[str, int]] = None,
        dev: Optional[Tuple[str, int]] = None,
        local: Optional[str] = None,
    ) -> None:
        """Update the internal version state."""
        if not (epoch or release):
            pre = pre or self.pre
            post = post or self.post
            dev = dev or self.dev
            local = local or self.local

        self._version = _Version(
            epoch=epoch or self.epoch,
            release=release or self.release,
            pre=pre,
            post=post,
            dev=dev,
            local=_parse_local_version(local) if local else None,
        )

        self._key = _cmpkey(
            self._version.epoch,
            self._version.release,
            self._version.pre,
            self._version.post,
            self._version.dev,
            self._version.local,
        )

    def bump_epoch(self) -> None:
        """Update epoch releaes for version system changes."""
        self.__update_version(epoch=self.epoch + 1)

    def bump_major(self) -> None:
        """Update major release to next version number."""
        self.__update_version(release=(self.major + 1, 0, 0))

    def bump_minor(self) -> None:
        """Update minor release to next version number."""
        self.__update_version(release=(self.major, self.minor + 1, 0))

    def bump_micro(self) -> None:
        """Update micro release to next version number."""
        self.__update_version(release=(self.major, self.minor, self.micro + 1))

    def __bump_version(self, kind: str) -> None:
        """Bump version based on version kind."""
        if kind == 'major':
            self.bump_major()
        if kind == 'minor':
            self.bump_minor()
        if kind == 'micro':
            self.bump_micro()

    def new_devrelease(self, kind: str = 'minor') -> None:
        """Update to the next development release version number."""
        if not self.dev:
            self.__bump_version(kind)
            self.__update_version(dev=('dev', 0))

    def bump_devrelease(self) -> None:
        """Update to the next development release version number."""
        if self.dev:
            dev = (self.dev[0], self.dev[1] + 1)
            self.__update_version(dev=dev)

    def new_local(self, name: str = 'build') -> None:
        """Create new local version instance number."""
        self.__update_version(local=f"{name}.0")

    def bump_local(self) -> None:
        """Update local version instance number."""
        if self.local:
            local = self.local.split('.')
            if local[-1].isdigit():
                local[-1] = str(int(local[-1]) + 1)
            self.__update_version(local='.'.join(local))

    def new_prerelease(self, kind: str = 'major') -> None:
        """Update to next prerelease version type."""
        if self.pre:
            if self.pre[0] == 'a':
                pre = ('b', 0)
            elif self.pre[0] == 'b':
                pre = ('rc', 0)
        else:
            self.__bump_version(kind)
            pre = ('a', 0)
        self.__update_version(pre=pre)

    def bump_prerelease(self) -> None:
        """Update the prerelease version number."""
        if self.pre:
            pre = (self.pre[0], self.pre[1] + 1)
            self.__update_version(pre=pre)

    def new_postrelease(self, kind: str = 'major') -> None:
        """Update to next prerelease version type."""
        if self.get_state() == 'final':
            self.__update_version(post=('post', 0))

    def bump_postrelease(self) -> None:
        """Update the post release version number."""
        if self.post:
            post = (self.post[0], self.post[1] + 1)
            self.__update_version(post=post)

    def finalize_release(self) -> None:
        """Update to next prerelease version type."""
        if self.is_devrelease or self.is_prerelease:
            self.__update_version(release=(self.major, self.minor, self.micro))
