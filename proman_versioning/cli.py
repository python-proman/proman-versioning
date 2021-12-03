# -*- coding: utf-8 -*-
# copyright: (c) 2021 by Jesse Johnson.
# license: MPL-2.0, see LICENSE for more details.
"""Control project versions."""

import logging
import sys
from typing import Optional

from proman_versioning import get_release_controller

log = logging.getLogger(__name__)
controller = get_release_controller()


def bump(
    commit: bool = False,
    release: bool = False,
    tag: bool = False,
    tag_name: Optional[str] = None,
    tag_message: Optional[str] = None,
    sign: bool = False,
    build: Optional[str] = None,
    dry_run: bool = False,
) -> None:
    """Manage project versions.

    Paramters
    ----------
    commit: bool
        Commit release changes to project.
    release: bool
        Make this version update a new release.
    tag: bool
        Tag this version.
    tag_name: str
        The tag name to use for this tag.
        default: version
    tag_message: str
        Notes included witht the tag.
    build: str
        Build version from other systems the may help coordinate build
        artifacts.
    dry_run: bool
        Run the command without making changes.
    """
    version = controller.bump_version(
        commit=commit,
        release=release,
        tag=tag,
        tag_name=tag_name,
        tag_message=tag_message,
        sign_tag=sign,
        build=build,
        dry_run=dry_run,
    )
    print(str(version), file=sys.stdout)


def view(release_type: bool = False, filepaths: bool = False) -> None:
    """Get the current version or settings of a project.

    Paramters
    ----------
    release_type: bool
        View the current release type
    filepaths: bool
        List the version filepaths
    """
    if release_type:
        print(controller.release, file=sys.stdout)
    if filepaths:
        for x in controller.config.templates:
            print(x['filepath'], file=sys.stdout)
    if not release_type and not filepaths:
        print(controller.config.version, file=sys.stdout)
