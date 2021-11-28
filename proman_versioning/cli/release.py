# -*- coding: utf-8 -*-
# copyright: (c) 2021 by Jesse Johnson.
# license: MPL-2.0, see LICENSE for more details.
"""Manage releases with VCS."""

import logging
import sys
from typing import Optional

from . import controller

log = logging.getLogger(__name__)


def start(
    kind: str = 'dev',
    commit: bool = True,
    dry_run: bool = False,
) -> None:
    """Start a release.

    Paramters
    ----------
    kind: str
        Choose the kind of release to be performed.
    commit: bool
        Commit release changes to project.
    """
    controller.start_release(kind=kind, commit=commit, dry_run=dry_run)
    print(f"project version is now: {controller.version}", file=sys.stdout)


def finish(
    commit: bool = True,
    tag: bool = False,
    tag_name: Optional[str] = None,
    tag_message: Optional[str] = None,
    sign_tag: bool = False,
    dry_run: bool = False,
) -> None:
    """Finish a release.

    Paramters
    ----------
    commit: bool
        Commit release changes to project.
    tag: bool
        Tag commit.
    tag_name: Optional[str]
        Name of tag commit.
    tag_message: Optional[str]
        Annotation of tag commit.
    sign_tag: bool
        Sign tag.
    """
    controller.finish_release(
        commit=commit,
        tag=tag,
        tag_name=tag_name,
        tag_message=tag_message,
        sign_tag=sign_tag,
    )
