# -*- coding: utf-8 -*-
# copyright: (c) 2021 by Jesse Johnson.
# license: MPL-2.0, see LICENSE for more details.
"""Control project versions."""

import logging
import sys
from typing import Optional

from . import controller

log = logging.getLogger(__name__)


def bump(
    commit: bool = False,
    tag: bool = False,
    tag_name: Optional[str] = None,
    tag_message: Optional[str] = None,
    sign: bool = False,
    build: Optional[str] = None,
    dry_run: bool = False,
) -> None:
    """Manage project versions."""
    version = controller.bump_version(
        commit=commit,
        tag=tag,
        tag_name=tag_name,
        tag_message=tag_message,
        sign_tag=sign,
        build=build,
        dry_run=dry_run,
    )
    print(str(version), file=sys.stdout)


def view(files: bool = False) -> None:
    """Get the current version of project."""
    if files:
        for x in controller.filepaths:
            print(x['filepath'], file=sys.stdout)
    else:
        print(controller.version, file=sys.stdout)
