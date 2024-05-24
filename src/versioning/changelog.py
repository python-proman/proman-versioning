"""Manage changelog using pygit2."""

import logging
import re
from collections import deque
from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, Generator, List, Tuple

from mdutils.mdutils import MdUtils  # pylint: disable=import-error

from versioning.grammars.conventional_commits import CommitMessageParser

if TYPE_CHECKING:
    from pygit2 import Commit, Repository

logging.getLogger(__name__).addHandler(logging.NullHandler())

SCOPES = ['added', 'changed', 'deprecated', 'removed', 'fixed', 'security']


class Changelog:
    """Manage changelog file."""

    def __init__(self, repo: 'Repository') -> None:
        """Initialize changelog."""
        self.repo = repo

    @property
    def tags(self) -> Generator['Commit', None, None]:
        """Get tagged commit."""
        # iterate tags and add each commit since preious tag to a section
        regex = re.compile('^refs/tags/')
        tags = [r for r in self.repo.references if regex.match(r)]
        for tag in tags:
            yield self.repo.revparse_single(tag)

    def _categorize_commit(self, commit: 'Commit') -> Tuple[str, List[str]]:
        """Get changes associated with a release."""
        parser = CommitMessageParser()
        parser.parse(commit.message.rstrip())
        # scope = parser.title['scope']
        row = [
            str(commit.id),
            parser.title['type'],
            parser.title['description'],
        ]

        if parser.title['type'] == 'feat':
            section = 'added'
        elif parser.title['type'] == 'fix':
            section = 'fixed'
        elif parser.title['type'] in (
            'refactor' 'ci' 'build' 'docs' 'test' 'style' 'perf'
        ):
            section = 'changed'
        else:
            section = 'misc'
        return section, row

    def generate_changelog(self) -> None:
        """Generate changelog."""
        # iterate tags and add each commit since preious tag to a section
        start_commit = self.repo.head.target

        releases = []
        commits = deque(self.repo.walk(start_commit))

        for tag in self.tags:
            tagged_commit = tag.get_object()
            changes: Dict[str, List[str]] = {
                'added': [],
                'changed': [],
                'deprecated': [],
                'removed': [],
                'fixed': [],
                'security': [],
                'misc': [],
            }

            while commits:
                commit = commits.pop()
                section, scope = self._categorize_commit(commit)
                changes[section].extend(scope)
                if tagged_commit == commit:
                    break

            releases.append(
                {
                    'name': tag.name,
                    'time': tag.tagger.time,
                    'changes': changes,
                }
            )
        self._generate_document(releases)

    def _generate_document(self, releases: List[Dict[str, Any]]) -> None:
        """Generate changelog file."""
        # stopgap until better parser is found
        md = MdUtils(
            file_name='CHANGELOG.md',
            title='Changelog',
            # author='Jesse P. Johnson'
        )
        md.new_header(level=1, title='ProMan Versioning Changelog')
        sections = ['commit', 'type', 'description']

        for release in reversed(releases):
            dt = datetime.fromtimestamp(release['time'])
            md.new_header(
                level=2,
                # title=f"[v{tag.name}]({url}) - ({dt.strftime('%Y-%m-%d')})"
                title=f"v{release['name']} - ({dt.strftime('%Y-%m-%d')})",
            )

            for k, v in release['changes'].items():
                if v != []:
                    md.new_header(level=3, title=k)
                    md.new_table(
                        columns=len(sections),
                        rows=len(sections + v) // len(sections),
                        text=sections + v,
                        text_align='left',
                    )
        md.create_md_file()
