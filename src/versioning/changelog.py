"""Manage changelog using pygit2."""

import logging
import re
from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, List

from mdutils.mdutils import MdUtils
from versioning.grammars.conventional_commits import CommitMessageParser

if TYPE_CHECKING:
    from pygit2 import Commit, Repository

logging.getLogger(__name__).addHandler(logging.NullHandler())

SCOPES = ['added', 'changed', 'deprecated', 'removed', 'fixed', 'security']


def get_release_changes(
    current_commit: 'Commit',
    repo: 'Repository'
) -> Dict[str, Any]:
    """Get changes associated with a release."""
    parser = CommitMessageParser()
    changes: Dict[str, List[str]] = {
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
            if scope not in changes:
                changes[scope] = []
            changes[scope].extend(row)
        elif parser.title['type'] == 'feat':
            changes['added'].extend(row)
        elif parser.title['type'] == 'fix':
            changes['fixed'].extend(row)
        elif (
            parser.title['type'] == 'refactor'
            or parser.title['type'] == 'ci'
            or parser.title['type'] == 'build'
            or parser.title['type'] == 'docs'
            or parser.title['type'] == 'test'
            or parser.title['type'] == 'style'
            or parser.title['type'] == 'perf'
        ):
            changes['changed'].extend(row)

        if current_commit == commit:
            break
    return changes


def generate_changelog(repo: 'Repository') -> None:
    """Provide main function."""
    # TODO: stopgap changelog solution
    md = MdUtils(
        file_name='CHANGELOG.md',
        title='Changelog',
        author='Jesse P. Johnson'
    )
    md.new_header(
        level=1,
        title='ProMan Versioning Changelog'
    )

    # iterate tags and add each commit since preious tag to a section
    regex = re.compile('^refs/tags/')
    tags = [r for r in repo.references if regex.match(r)]
    for tag in reversed(tags):
        # get commit from tag
        obj = repo.revparse_single(tag)
        current_commit = obj.get_object()

        # baseurl = 'https://gitlab.mgmt.hijynx.io/primistek/changelog'
        # url = f"{baseurl}/-/tree/{obj.name}/"
        dt = datetime.fromtimestamp(obj.tagger.time)
        md.new_header(
            level=2,
            # title=f"[v{obj.name}]({url}) - ({dt.strftime('%Y-%m-%d')})"
            title=f"v{obj.name} - ({dt.strftime('%Y-%m-%d')})"
        )

        sections = ['commit', 'type', 'description']
        changes = get_release_changes(current_commit, repo)

        for k, v in changes.items():
            if v != []:
                md.new_header(level=3, title=k)
                md.new_table(
                    columns=len(sections),
                    rows=len(sections + v) // len(sections),
                    text=sections + v,
                    text_align='left',
                )
    md.create_md_file()
