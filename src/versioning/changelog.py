"""Manage changelog using pygit2."""

import logging
import os
import re
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Set  # noqa

from mdutils.mdutils import MdUtils
from pygit2 import discover_repository, Repository
from versioning import get_release_controller
from versioning.grammars.conventional_commits import CommitMessageParser

logging.getLogger(__name__).addHandler(logging.NullHandler())

SCOPES = ['added', 'changed', 'deprecated', 'removed', 'fixed', 'security']
_controller = get_release_controller()


def generate_changelog() -> None:
    """Provide main function."""
    # TODO: stopgap changelog solution
    md = MdUtils(
        file_name='CHANGELOG.md',
        title='Changelog',
        author='Jesse P. Johnson'
    )

    repo = Repository(discover_repository(os.getcwd()))
    # print(list(repo.references))

    md.new_header(
        level=1,
        title='ProMan Versioning Changelog'
    )

    # iterate tags and add each commit since preious tag to a section
    regex = re.compile('^refs/tags/')
    tags = [r for r in repo.references if regex.match(r)]
    # previous_tag = None
    for tag in reversed(tags):
        obj = repo.revparse_single(tag)
        baseurl = 'https://gitlab.mgmt.hijynx.io/primistek/changelog'
        url = f"{baseurl}/-/tree/{obj.name}/"
        dt = datetime.fromtimestamp(obj.tagger.time)
        md.new_header(
            level=2,
            title=f"[v{obj.name}]({url}) - ({dt.strftime('%Y-%m-%d')})"
        )

        parser = CommitMessageParser()
        # NOTE: use this to get commit from tag
        # current_commit = obj.get_object()

        sections = ['commit', 'type', 'description']
        scopes: Dict[str, List[str]] = {
            'added': [],
            'changed': [],
            'deprecated': [],
            'removed': [],
            'fixed': [],
            'security': [],
        }
        for commit in repo.walk(repo.head.target):
            # check if commit is tagged and stop if it is
            parser.parse(commit.message.rstrip())
            scope = parser.title['scope']
            row = [
                commit.hex,
                parser.title['type'],
                parser.title['description']
            ]

            if scope is not None:
                if scope not in scopes:
                    scopes[scope] = []
                scopes[scope].extend(row)
            elif parser.title['type'] == 'feat':
                scopes['added'].extend(row)
            elif parser.title['type'] == 'fix':
                scopes['fixed'].extend(row)
            elif (
                parser.title['type'] == 'refactor'
                or parser.title['type'] == 'ci'
                or parser.title['type'] == 'build'
                or parser.title['type'] == 'docs'
                or parser.title['type'] == 'test'
                or parser.title['type'] == 'style'
                or parser.title['type'] == 'perf'
            ):
                scopes['changed'].extend(row)

        for k, v in scopes.items():
            if v != []:
                md.new_header(level=3, title=k)
                md.new_table(
                    columns=len(sections),
                    rows=len(sections + v) // len(sections),
                    text=sections + v,
                    text_align='left',
                )
        # print('type', obj.type_str)
        # print('hash', obj.hex)
        # previous_tag = tag
        # print('previous tag:', previous_tag)
    md.create_md_file()
