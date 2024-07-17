# copyright: (c) 2021 by Jesse Johnson.
# license: LGPL-3.0, see LICENSE.md for more details.
"""Manage version numbers."""

# import logging
from dataclasses import InitVar, asdict, dataclass, field
from typing import Any, Dict, List, Optional, Tuple, Union

from packaging.version import Version as PackageVersion
from packaging.version import _cmpkey, _parse_local_version, _Version
from transitions import Machine

# from transitions.extensions import HierarchicalMachine


@dataclass
class LocalConfig:
    """Manage local build versions."""

    states: List[Union[str, Dict[str, Any]]] = field(default_factory=list)
    transitions: List[Dict[str, Any]] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Initialize local version configuration."""
        self.states = ['non_local', 'local']

        # add build number
        self.transitions.append(
            {
                'trigger': 'update_local',
                'source': 'non_local',
                'dest': 'local',
                'before': '_update_local',
            }
        )

        # update build number
        self.transitions.append(
            {
                'trigger': 'update_local',
                'source': 'local_local',
                'dest': '',
                'before': '_update_local',
            }
        )

        # remove build number
        self.transitions.append(
            {
                'trigger': 'update_local',
                'source': 'local',
                'dest': 'non_local',
                'before': '_update_local',
            }
        )


@dataclass
class ReleaseConfig:
    """Manage versioning flow."""

    default_release_type: InitVar[str]
    states: List[Union[str, Dict[str, Any]]] = field(default_factory=list)
    transitions: List[Dict[str, Any]] = field(default_factory=list)

    def __post_init__(self, default_release_type: str) -> None:
        """Initialize versioning config."""
        self.states = ['dev', 'alpha', 'beta', 'candidate', 'final', 'post']

        # XXX: need to calver as alternative first
        # self.transitions.append(
        #     {
        #         'trigger': 'bump_epoch',
        #         'source': '*',
        #         'dest': default_release_type,
        #         'before': '_bump_epoch',
        #         'after': 'new_release',
        #         'conditions': ['autostart_default_release'],
        #     }
        # )

        self.transitions.append(
            {
                'trigger': 'bump_major',
                'source': '*',
                'dest': default_release_type,
                'before': '_bump_major',
                'after': 'new_release',
                'conditions': ['autostart_default_release'],
            }
        )

        self.transitions.append(
            {
                'trigger': 'bump_minor',
                'source': '*',
                'dest': default_release_type,
                'before': '_bump_minor',
                'after': 'new_release',
                'conditions': ['autostart_default_release'],
            }
        )

        self.transitions.append(
            {
                'trigger': 'bump_micro',
                'source': '*',
                'dest': default_release_type,
                'before': '_bump_micro',
                'after': 'new_release',
                'conditions': ['autostart_default_release'],
            }
        )

        self.transitions.append(
            {
                'trigger': 'bump_epoch',
                'source': '*',
                'dest': 'final',
                'before': '_bump_epoch',
                # 'unless': ['autostart_default_release'],
            }
        )

        self.transitions.append(
            {
                'trigger': 'bump_major',
                'source': '*',
                'dest': 'final',
                'before': '_bump_major',
                'unless': ['autostart_default_release'],
            }
        )

        self.transitions.append(
            {
                'trigger': 'bump_minor',
                'source': '*',
                'dest': 'final',
                'before': '_bump_minor',
                'unless': ['autostart_default_release'],
            }
        )

        self.transitions.append(
            {
                'trigger': 'bump_micro',
                'source': '*',
                'dest': 'final',
                'before': '_bump_micro',
                'unless': ['autostart_default_release'],
            }
        )

        # development releases
        self.transitions.append(
            {
                'trigger': 'start_release',
                'source': ['final', 'post'],
                'dest': 'dev',
                'before': '_new_devrelease',
                'conditions': ['enable_devreleases'],
            }
        )

        # pre-releases
        self.transitions.append(
            {
                'trigger': 'start_release',
                'source': ['final', 'post'],
                'dest': 'alpha',
                'before': '_new_prerelease',
                'conditions': ['enable_prereleases'],
                'unless': ['enable_devreleases'],
            }
        )
        self.transitions.append(
            {
                'trigger': 'start_release',
                'source': 'dev',
                'dest': 'alpha',
                'before': '_new_prerelease',
                'conditions': ['enable_devreleases', 'enable_prereleases'],
            }
        )
        self.transitions.append(
            {
                'trigger': 'start_release',
                'source': 'alpha',
                'dest': 'beta',
                'before': '_new_prerelease',
                'conditions': ['enable_prereleases'],
            }
        )
        self.transitions.append(
            {
                'trigger': 'start_release',
                'source': 'beta',
                'dest': 'candidate',
                'before': '_new_prerelease',
                'conditions': ['enable_prereleases'],
            }
        )

        # final release
        self.transitions.append(
            {
                'trigger': 'start_release',
                'source': 'dev',
                'dest': 'final',
                'before': '_finalize_release',
                'conditions': ['enable_devreleases'],
                'unless': ['enable_prereleases'],
            }
        )

        self.transitions.append(
            {
                'trigger': 'start_release',
                'source': 'candidate',
                'dest': 'final',
                'before': '_finalize_release',
                'conditions': ['enable_prereleases'],
            }
        )
        self.transitions.append(
            {
                'trigger': 'start_release',
                'source': 'post',
                'dest': 'final',
                'before': '_finalize_release',
                'conditions': ['enable_postreleases'],
                'unless': ['enable_devreleases', 'enable_prereleases'],
            }
        )

        # post-releases
        self.transitions.append(
            {
                'trigger': 'start_postrelease',
                'source': 'final',
                'dest': 'post',
                'before': '_new_postrelease',
                'conditions': ['enable_postreleases'],
            }
        )

        # bump release number
        self.transitions.append(
            {
                'trigger': 'bump_release',
                'source': '*',
                'dest': None,
                'before': '_bump_release',
            }
        )


class Version(PackageVersion):
    """Provide PEP440 compliant versioning."""

    def __init__(self, version: str, **kwargs: Any) -> None:
        """Initialize version object."""
        self.compat = kwargs.pop('compat', 'pep440')
        super().__init__(version=version)

        # TODO: transitions here should be populated by VCS workflow

        self.enable_devreleases = kwargs.get('enable_devreleases', True)
        self.enable_prereleases = kwargs.get('enable_prereleases', True)
        self.enable_postreleases = kwargs.get('enable_postreleases', True)
        self.autostart_default_release = kwargs.get(
            'autostart_default_release', True
        )

        _release = ReleaseConfig(
            default_release_type=self.default_release_type,
        )
        self.machine = Machine(
            self,
            **asdict(_release),
            initial=self.release_type,
        )
        self.local_machine = Machine(
            self,
            **asdict(LocalConfig()),
            initial='local' if self.local else 'non_local',
            model_attribute='build',
        )

        self.machine.auto_transitions = False

    def __str__(self) -> str:
        """Handle version formatting."""
        parts = []

        # Epoch
        if self.epoch != 0:
            parts.append(f"{self.epoch}!")

        # Release segment
        parts.append('.'.join(str(x) for x in self.release))

        # Pre-release
        if self.pre is not None:
            if self.compat == 'semver':
                prefix = '-'
            elif self.compat == 'pep440':
                prefix = ''
            elif self.compat == 'numeric':
                prefix = '.'
            parts.append(f"{prefix}{self.pre[0]}{str(self.pre[1])}")

        # Post-release
        elif self.post is not None:
            if self.compat == 'pep440':
                prefix = '.post'
            elif self.compat == 'semver':
                prefix = '-'
            elif self.compat == 'numeric':
                prefix = '.'
            parts.append(f"{prefix}{self.post}")

        # Development release
        if self.dev is not None:
            if self.compat == 'pep440' or (
                self.compat == 'semver'
                and (self.pre is not None or self.post is not None)
            ):
                prefix = '.dev'
            elif self.compat == 'semver':
                prefix = '-dev'
            elif self.compat == 'numeric':
                prefix = '.'
            parts.append(f"{prefix}{self.dev}")

        # Local version segment
        if self.local is not None:
            parts.append(f"+{self.local}")

        return ''.join(parts)

    @property
    def release_type(self) -> str:
        """Get the current state of package release."""
        if self.is_devrelease:
            state = 'dev'
        elif self.is_prerelease and self.pre:
            if self.pre[0] == 'a':
                return 'alpha'
            if self.pre[0] == 'b':
                return 'beta'
            if self.pre[0] == 'rc':
                return 'candidate'
        elif self.is_postrelease:
            state = 'post'
        else:
            state = 'final'
        return state

    @property
    def default_release_type(self) -> str:
        """Get the starting release type."""
        if self.enable_devreleases:
            return 'dev'
        if self.enable_prereleases:
            return 'alpha'
        return 'final'

    @property
    def query(self) -> str:
        """Get PEP-440 compliant regex query for version."""
        r = '.'.join(str(x) for x in self.release)
        if self.dev:
            v = f"{r}[-_\\.]?dev[-_\\.]?{self.dev or '0?'}"
            return v

        if self.pre:
            if self.epoch > 0:
                v = f"{self.epoch}!{r}"
            (pre, inst) = self.pre
            if pre == 'a':
                v = f"{r}[-_\\.]?(?:a|alpha)[-_\\.]?{inst or '0?'}"
            if pre == 'b':
                v = f"{r}[-_\\.]?(?:b|beta)[-_\\.]?{inst or '0?'}"
            if pre == 'rc':
                candidate = 'c|candidate|rc|release'
                v = f"{r}[-_\\.]?(?:{candidate})[-_\\.]?{inst or '0?'}"
            return v
        if self.post:
            v = f"{r}[-_\\.]?(?:post[-_\\.]?)?{self.post}"
            return v
        return str(self)

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
            post = post or (None if self.post is None else ('post', self.post))
            dev = dev or (None if self.dev is None else ('dev', self.dev))

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

    def _bump_epoch(self) -> None:
        """Update epoch releaes for version system changes."""
        self.__update_version(epoch=self.epoch + 1)

    def _bump_major(self) -> None:
        """Update major release to next version number."""
        self.__update_version(release=(self.major + 1, 0, 0))

    def _bump_minor(self) -> None:
        """Update minor release to next version number."""
        self.__update_version(release=(self.major, self.minor + 1, 0))

    def _bump_micro(self) -> None:
        """Update micro release to next version number."""
        self.__update_version(release=(self.major, self.minor, self.micro + 1))

    def __bump_version(self, segment: str) -> None:
        """Bump version based on version kind."""
        if segment == 'epoch':
            self._bump_epoch()
        if segment == 'major':
            self._bump_major()
        if segment == 'minor':
            self._bump_minor()
        if segment == 'micro':
            self._bump_micro()

    def _new_devrelease(self, segment: Optional[str] = None) -> None:
        """Update to the next development release version number."""
        if self.dev is None:
            if segment:
                self.__bump_version(segment)
            self.__update_version(dev=('dev', 0))

    def _new_prerelease(self, segment: Optional[str] = None) -> None:
        """Update to next prerelease version type."""
        if self.pre is not None:
            if self.pre[0] == 'a':
                pre = ('b', 0)
            elif self.pre[0] == 'b':
                pre = ('rc', 0)
        else:
            if segment:
                self.__bump_version(segment)
            pre = ('a', 0)
        self.__update_version(pre=pre)

    def _new_postrelease(self) -> None:
        """Update the post release version number."""
        if self.release_type == 'final':
            self.__update_version(post=('post', 0))

    def new_release(
        self,
        segment: Optional[str] = None,
        kind: Optional[str] = None,
    ) -> None:
        """Update the version release."""
        kind = kind or self.default_release_type
        if self.enable_devreleases and kind == 'dev':
            self._new_devrelease(segment=segment)
        if kind == 'alpha':
            self._new_prerelease(segment=segment)
        if kind == 'final':
            self._finalize_release()

    def _bump_release(self, *args: Any, **kwargs: Any) -> None:
        """Update to the next development release version number."""
        if self.enable_devreleases and self.dev is not None:
            dev = self.dev + 1
            self.__update_version(dev=('dev', dev))
        elif self.enable_prereleases and self.pre is not None:
            pre = (self.pre[0], self.pre[1] + 1)
            self.__update_version(pre=pre)
        elif self.enable_postreleases:
            if self.release_type == 'final':
                self.__update_version(post=('post', 0))
            elif self.post is not None:
                post = self.post + 1
                self.__update_version(post=('post', post))

    def _new_local(self, local: str) -> None:
        """Create new local version instance number."""
        self.__update_version(local=local)

    def _finalize_release(self, segment: Optional[str] = None) -> None:
        """Update to next prerelease version type."""
        self.__update_version(release=(self.major, self.minor, self.micro))
