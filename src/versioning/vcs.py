# copyright: (c) 2021 by Jesse Johnson.
# license: LGPL-3.0, see LICENSE.md for more details.
"""Parse git commit messages."""

# import logging
import os
from typing import Any, List, Optional

from pygit2 import (
    GIT_OBJECT_COMMIT,
    Commit,
    RemoteCallbacks,
    Repository,
    Signature,
    Tag,
    UserPass,
)

from versioning.exception import VersioningException


class Git:
    """Provide settings for git repositories."""

    def __init__(self, repo: Repository) -> None:
        """Initialize git object."""
        self.repo = repo
        self.hooks_dir = os.path.join(self.repo.path, 'hooks')
        self.config = os.path.join(self.repo.path, 'config')

    @property
    def username(self) -> str:
        """Return username from git configuration."""
        try:
            return self.repo.config['user.name']
        except Exception as exc:
            raise VersioningException('git user.name not configured') from exc

    @property
    def branch(self) -> str:
        """Return branch name of current branch."""
        return self.repo.head.shorthand

    @property
    def email(self) -> str:
        """Return email from git configuration."""
        try:
            return self.repo.config['user.email']
        except Exception as exc:
            raise VersioningException('git user.email not configured') from exc

    @property
    def repo_dir(self) -> str:
        """Return directory of repository."""
        return self.repo.path

    @property
    def working_dir(self) -> str:
        """Return working directory of project."""
        return os.path.abspath(os.path.join(self.repo_dir, os.pardir))

    @property
    def ref(self) -> str:
        """Retrieve the current reference."""
        return self.repo.head.name

    def add_remote(
        self,
        name: str,
        url: str,
        fetch: Optional[str] = None,
        # **kwargs: Any,
    ) -> None:
        """Add remote."""
        if name not in [x.name for x in self.repo.remotes]:
            if fetch is None:
                fetch = f"+refs/heads/*:refs/remotes/{name}/*"
            self.repo.remotes.create(name, url, fetch)
        elif self.repo.remotes[name].url != url:
            self.repo.remotes.set_url(name, url)

    def commit(
        self,
        branch: Optional[str] = None,
        filepaths: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> Optional[Commit]:
        """Create commit."""
        ref = f"refs/heads/{branch}" if branch else self.ref

        author = Signature(self.username, self.email)
        committer = kwargs.get('commiter', author)
        message = kwargs.get('message', 'ci: bump version')

        # populate index
        index = self.repo.index
        if not filepaths:
            index.add_all()
        else:
            for filepath in filepaths:
                index.add(
                    os.path.relpath(
                        filepath, os.path.join(self.repo.path, os.pardir)
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
                ref,
                author,
                committer,
                message,
                tree,
                parents,
                encoding,
            )
            return commit
        # TODO: should a mock commit be created?
        return None

    def tag(
        self, name: str, branch: Optional[str] = None, **kwargs: Any
    ) -> Optional[Tag]:
        """Create tag."""
        ref = f"refs/heads/{branch}" if branch else self.ref
        commit = self.repo.resolve_refish(ref)[0]
        oid = str(commit.id)
        kind = kwargs.get('kind', GIT_OBJECT_COMMIT)

        # tagger = pygit2.Signature('Alice Doe', 'adoe@example.com', 12347, 0)
        tagger = Signature(self.username, self.email)
        message = kwargs.get('message')
        if not kwargs.get('dry_run', False):
            tag = self.repo.create_tag(
                name, oid, kind, tagger, message or f"ci: {name}"
            )
            return tag
        # TODO: should a mock tag be created?
        return None

    def push(
        self,
        branch: Optional[str] = None,
        remote: str = 'origin',
        remote_branch: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
    ) -> None:
        """Push commited changes."""
        # TODO: feels like remote should be encapsulated with creds
        remote_branch = remote_branch or branch or self.ref.split('/')[-1]
        # ref = f"refs/heads/{branch}" if branch else self.ref
        # remote_ref = f"refs/remotes/{remote}/{remote_branch}"
        # print(ref, remote_ref)

        remote_repo = self.repo.remotes[remote]
        credentials = UserPass(username or self.username, password)
        remote_repo.credentials = credentials

        callbacks = RemoteCallbacks(credentials=credentials)
        remote_repo.push([f"refs/heads/{branch}"], callbacks=callbacks)
