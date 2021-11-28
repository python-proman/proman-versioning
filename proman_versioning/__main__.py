# -*- coding: utf-8 -*-
# copyright: (c) 2021 by Jesse Johnson.
# license: MPL-2.0, see LICENSE for more details.
"""Provide CLI management."""

from argufy import Parser

from proman_versioning.cli import version, release


def main() -> None:
    """Provide CLI for git-tools."""
    parser = Parser()
    parser.add_commands(release, command_type='subcommand')
    parser.add_commands(version)
    parser.dispatch()


if __name__ == '__main__':
    main()
