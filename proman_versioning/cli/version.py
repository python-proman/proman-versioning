# -*- coding: utf-8 -*-
# copyright: (c) 2020 by Jesse Johnson.
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
    name: Optional[str] = None,
    message: Optional[str] = None,
    sign: bool = False,
    dry_run: bool = False,
) -> None:
    """Manage project versions."""
    controller.bump_version(
        commit=commit,
        tag=tag,
        tag_name=name,
        tag_message=message,
        sign_tag=sign,
        dry_run=dry_run,
    )
    print(controller.version, file=sys.stdout)


def view() -> None:
    """Get the current version of project."""
    print(controller.version, file=sys.stdout)
