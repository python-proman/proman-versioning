# copyright: (c) 2021 by Jesse Johnson.
# license: MPL-2.0, see LICENSE for more details.
"""Manage version numbers."""

# import logging
from dataclasses import InitVar, asdict, dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from packaging.version import Version as PackageVersion
from packaging.version import _cmpkey, _parse_local_version, _Version
from transitions import Machine


@dataclass
class ReleaseMachine:
    """Manage versioning flow."""

    initial: str
    default_release_type: InitVar[str]
    states: List[str] = field(default_factory=list)
    transitions: List[Dict[str, Any]] = field(default_factory=list)

    def __post_init__(
        self,
        default_release_type: str,
    ) -> None:
        """Initialize versioning config."""
        self.states = [
            'development', 'alpha', 'beta', 'release', 'final', 'post'
        ]

        self.transitions = []

        # XXX: need to calver as alternative first
        # self.transitions.append(
        #     dict(
        #         trigger='bump_epoch',
        #         source='*',
        #         dest=default_release_type,
        #         before='_bump_epoch',
        #         after='new_release',
        #         conditions=['autostart_default_release'],
        #     )
        # )

        self.transitions.append(
            dict(
                trigger='bump_major',
                source='*',
                dest=default_release_type,
                before='_bump_major',
                after='new_release',
                conditions=['autostart_default_release'],
            )
        )

        self.transitions.append(
            dict(
                trigger='bump_minor',
                source='*',
                dest=default_release_type,
                before='_bump_minor',
                after='new_release',
                conditions=['autostart_default_release'],
            )
        )

        self.transitions.append(
            dict(
                trigger='bump_micro',
                source='*',
                dest=default_release_type,
                before='_bump_micro',
                after='new_release',
                conditions=['autostart_default_release'],
            )
        )

        self.transitions.append(
            dict(
                trigger='bump_epoch',
                source='*',
                dest='final',
                before='_bump_epoch',
                # unless=['autostart_default_release'],
            )
        )

        self.transitions.append(
            dict(
                trigger='bump_major',
                source='*',
                dest='final',
                before='_bump_major',
                unless=['autostart_default_release'],
            )
        )

        self.transitions.append(
            dict(
                trigger='bump_minor',
                source='*',
                dest='final',
                before='_bump_minor',
                unless=['autostart_default_release'],
            )
        )

        self.transitions.append(
            dict(
                trigger='bump_micro',
                source='*',
                dest='final',
                before='_bump_micro',
                unless=['autostart_default_release'],
            )
        )

        # development releases
        self.transitions.append(
            dict(
                trigger='start_release',
                source=['final', 'post'],
                dest='development',
                before='_new_devrelease',
                conditions=['enable_devreleases'],
            )
        )

        # pre-releases
        self.transitions.append(
            dict(
                trigger='start_release',
                source=['final', 'post'],
                dest='alpha',
                before='_new_prerelease',
                conditions=['enable_prereleases'],
                unless=['enable_devreleases'],
            )
        )
        self.transitions.append(
            dict(
                trigger='start_release',
                source=['development'],
                dest='alpha',
                before='_new_prerelease',
                conditions=['enable_devreleases', 'enable_prereleases'],
            )
        )
        self.transitions.append(
            dict(
                trigger='start_release',
                source='alpha',
                dest='beta',
                before='_new_prerelease',
                conditions=['enable_prereleases'],
            )
        )
        self.transitions.append(
            dict(
                trigger='start_release',
                source='beta',
                dest='release',
                before='_new_prerelease',
                conditions=['enable_prereleases'],
            )
        )

        # final release
        self.transitions.append(
             dict(
                 trigger='finish_release',
                 source=['development'],
                 dest='final',
                 before='finalize_release',
                 conditions=['enable_devreleases'],
                 unless=['enable_prereleases'],
             )
        )

        self.transitions.append(
             dict(
                 trigger='finish_release',
                 source=['release'],
                 dest='final',
                 before='finalize_release',
                 conditions=['enable_prereleases'],
             )
        )
        self.transitions.append(
             dict(
                 trigger='finish_release',
                 source=['post'],
                 dest='final',
                 before='finalize_release',
                 conditions=['enable_postreleases'],
                 unless=['enable_devreleases', 'enable_prereleases'],
             )
        )

        # post-releases
        self.transitions.append(
            dict(
                trigger='start_postrelease',
                source='final',
                dest='post',
                before='_new_postrelease',
                conditions=['enable_postreleases'],
            )
        )

        # bump release number
        self.transitions.append(
            dict(
                trigger='bump_release',
                source='*',
                dest=None,
                before='_bump_release',
            )
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

        config = ReleaseMachine(
            initial=self.release_type,
            default_release_type=self.default_release_type,
        )
        self.machine = Machine(self, **asdict(config))
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
                separator = '-'
            else:
                separator = ''
            parts.append(
                f"{separator}{self.pre[0]}{str(self.pre[1])}"
            )

        # Post-release
        if self.post is not None:
            if self.compat == 'semver':
                separator = '-'
            else:
                separator = '.post'
            parts.append(f"{separator}{self.post}")

        # Development release
        if self.dev is not None:
            if self.compat == 'semver':
                separator = '-'
            else:
                separator = '.'
            parts.append(f"{separator}dev{self.dev}")

        # Local version segment
        if self.local is not None:
            parts.append(f"+{self.local}")

        return ''.join(parts)

    @property
    def release_type(self) -> str:
        """Get the current state of package release."""
        if self.is_devrelease:
            state = 'development'
        elif self.is_prerelease and self.pre:
            if self.pre[0] == 'a':
                return 'alpha'
            elif self.pre[0] == 'b':
                return 'beta'
            elif self.pre[0] == 'rc':
                return 'release'
        elif self.is_postrelease:
            state = 'post'
        else:
            state = 'final'
        return state

    @property
    def default_release_type(self) -> str:
        """Get the starting release type."""
        if self.enable_devreleases:
            return 'development'
        elif self.enable_prereleases:
            return 'alpha'
        else:
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
        elif self.post:
            v = f"{r}[-_\\.]?(?:post[-_\\.]?)?{self.post}"
            return v
        else:
            return str(self)

    def __update_version(
        self,
        epoch: Optional[int] = None,
        release: Optional[Tuple[Any, ...]] = None,
        pre: Optional[Tuple[str, Optional[int]]] = None,
        post: Optional[Tuple[Optional[str], Optional[int]]] = None,
        dev: Optional[Tuple[str, Optional[int]]] = None,
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
        if self.enable_devreleases and kind == 'development':
            self._new_devrelease(segment=segment)
        if kind == 'alpha':
            self._new_prerelease(segment=segment)
        if kind == 'final':
            self.finalize_release()

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

    def new_local(self, local: str) -> None:
        """Create new local version instance number."""
        self.__update_version(local=local)

    def finalize_release(self) -> None:
        """Update to next prerelease version type."""
        if self.is_devrelease or self.is_prerelease:
            self.__update_version(release=(self.major, self.minor, self.micro))
