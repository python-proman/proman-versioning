# copyright: (c) 2021 by Jesse Johnson.
# license: LGPL-3.0, see LICENSE.md for more details.
"""Provide CLI management."""

from argufy import Parser

from versioning import __version__, cli


def main() -> None:
    """Provide CLI for git-tools."""
    parser = Parser(version=__version__)
    parser.add_commands(cli)
    parser.dispatch()


if __name__ == '__main__':
    main()
