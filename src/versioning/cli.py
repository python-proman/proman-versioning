# copyright: (c) 2021 by Jesse Johnson.
# license: LGPL-3.0, see LICENSE.md for more details.
"""Control project versions."""

import logging
import sys
from typing import Optional

from versioning import get_release_controller

_log = logging.getLogger(__name__)
_controller = get_release_controller()


def bump(
    commit: bool = False,
    message: Optional[str] = None,
    tag: bool = False,
    tag_name: Optional[str] = None,
    # sign: bool = False,
    release: bool = False,
    build: Optional[str] = None,
    dry_run: bool = False,
) -> None:
    """Update project version.

    Parameters
    ----------
    build: str
        Build version from other systems the may help coordinate build
        artifacts.
    commit: bool
        Commit release changes to project.
    dry_run: bool
        Run the command without making changes.
    message: str
        Notes included with the commit.
    release: bool
        Make this version a new release.
    tag: bool
        Tag this version.
    tag_name: str
        The tag name to use for this tag.

    """
    # sign: bool
    #     Sign commit with PKI signature.
    version = _controller.update_version(
        commit=commit,
        release=release,
        tag=tag,
        tag_name=tag_name,
        # sign_tag=sign,
        message=message,
        build=build,
        dry_run=dry_run,
    )
    print(str(version), file=sys.stdout)


def info(release: bool = False, filepaths: bool = False) -> None:
    """Get current version project.

    Parameters
    ----------
    release: bool
        View the current release type
    filepaths: bool
        List the version filepaths

    """
    if release:
        print(_controller.release, file=sys.stdout)
    if filepaths:
        for x in _controller.config.templates:
            print(x['filepath'], file=sys.stdout)
    if not release and not filepaths:
        print(_controller.config.version, file=sys.stdout)


def push(
    remote: str = 'origin',
    remote_branch: Optional[str] = None,
    remote_url: Optional[str] = None,
    username: Optional[str] = None,
    password: Optional[str] = None,
) -> None:
    """Push project version.

    Parameters
    ----------
    remote: str
        The reference name of the repository.
    remote_branch: str
        The branch name of the remote reference.
    remote_url: str
        Remote URL of the repository.
    username: str
        Username for access to remote repository.
    password: str
        Password for access to remote repository.

    """
    # INFO: Helper for when run from containers without git.
    _controller.push_changes(
        remote=remote,
        remote_branch=remote_branch,
        remote_url=remote_url,
        username=username,
        password=password,
    )
