# copyright: (c) 2021 by Jesse Johnson.
# license: LGPL-3.0, see LICENSE.md for more details.
"""Handle commit workflows for conentional commits."""

from typing import TYPE_CHECKING

from rich.prompt import Prompt

if TYPE_CHECKING:
    from versioning.config import Config


def prepare_commit(config: 'Config') -> str:
    """Prepare commit message."""
    name = Prompt.ask(
        "Enter your name",
        choices=["Paul", "Jessica", "Duncan"],
        default="Paul",
    )
    return name
