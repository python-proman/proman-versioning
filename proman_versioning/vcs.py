# -*- coding: utf-8 -*-
# copyright: (c) 2020 by Jesse Johnson.
# license: MPL-2.0, see LICENSE for more details.
"""Parse Git commit messages."""

# import logging
import os
from typing import Any, List, Optional

from pygit2 import GIT_OBJ_COMMIT, Commit, Repository, Signature, Tag

# from proman_versioning import exception


class Git:
    """Provide settings for git repositories."""

    system_config: str = os.path.join(os.sep, 'etc', 'gitconfig')
    global_config: str = os.path.join(os.path.expanduser('~'), '.gitconfig')

    def __init__(self, repo: Repository) -> None:
        """Initialize git object."""
        self.repo = repo
        self.ref = 'HEAD'
        self.hooks_dir = os.path.join(self.repo.path, 'hooks')
        self.config = os.path.join(self.repo.path, 'config')

    @property
    def base_dir(self) -> str:
        """Return base directory of repository."""
        return self.repo.path

    @property
    def working_dir(self) -> str:
        """Return working directory of project."""
        return os.path.abspath(os.path.join(self.repo.path, '..'))

    @property
    def branch(self) -> str:
        """Retrieve the current branch."""
        return self.repo.head.name

    def commit(
        self,
        name: Optional[str] = None,
        filepaths: List[str] = [],
        **kwargs: Any,
    ) -> Commit:
        """Create commit."""
        if not name:
            name = f"refs/heads/{self.ref}"

        # TODO: pull from gitconfig or prompt
        author = Signature('Jesse P. Johson', 'jpj6652@gmail.com')
        committer = kwargs.get('commiter', author)
        message: str = kwargs.get('message', 'ci: generated commit')

        # populate index
        index = self.repo.index
        if filepaths == []:
            index.add_all()
        else:
            for filepath in filepaths:
                index.add(
                    os.path.relpath(
                        filepath, os.path.join(self.repo.path, '..')
                    )
                )
        index.write()
        tree = index.write_tree()

        # get parent
        parents = kwargs.get('parents', [self.repo.head.target])
        encoding = kwargs.get('encoding', 'utf-8')

        # commit
        if not kwargs.get('dry_run', False):
            commit = self.repo.create_commit(
                name,
                author,
                committer,
                message,
                tree,
                parents,
                encoding,
            )
        return commit

    def tag(self, name: str, ref: str = 'HEAD', **kwargs: Any) -> Tag:
        """Create tag."""
        commit = self.repo.resolve_refish(ref)[0]
        oid = commit.hex
        kind = kwargs.get('kind', GIT_OBJ_COMMIT)
        signature = kwargs.get('signature', commit.signature)
        message = kwargs.get('message', f"ci: {name}")
        if not kwargs.get('dry_run', False):
            tag = self.repo.create_tag(name, oid, kind, signature, message)
        return tag
