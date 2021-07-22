# -*- coding: utf-8 -*-
# copyright: (c) 2020 by Jesse Johnson.
# license: Apache 2.0, see LICENSE for more details.
'''Parse Git commit messages.'''

# import logging
import os
from typing import Any, List, Optional

from git import Repo

from proman_releases import exception

# from git.types import PathLike
# from transitions import Machine


class Git:
    '''Provide settings for git repositories.'''

    system_config: str = os.path.join(os.sep, 'etc', 'gitconfig')
    global_config: str = os.path.join(os.path.expanduser('~'), '.gitconfig')

    def __init__(self, repo: Repo) -> None:
        '''Initialize git object.'''
        self.branch = 'master'
        self.repo = repo
        self.hooks_dir = os.path.join(self.repo.git_dir, 'hooks')
        self.config = os.path.join(self.repo.git_dir, 'config')

    def init(self, path: str) -> None:
        '''Initialize a Git repository.'''
        if not os.path.exists(os.path.join(path, '.git')):
            Repo.init(path)
        else:
            print('repository already initialized')

    def clone(
        self,
        url: str,
        path: str = '.',
        branch: str = 'master',
    ) -> None:
        '''Clone Git repository.'''
        if not os.path.exists(path):
            Repo.clone_from(url, path, branch=branch)
        else:
            raise exception.PromanWorkflowException(
                'cloned repository alreaady exists'
            )

    def add_remote(
        self,
        url: str,
        remote: str = 'origin',
        branch: str = 'master',
    ) -> None:
        '''Add Git remote repository URL.'''
        if next(iter(self.repo.remotes), None) is None:
            self.repo.create_remote(remote, url=url)
        else:
            for r in self.repo.remotes:
                if remote == r.name:
                    r.set_url(self.repo)
                else:
                    self.repo.create_remote(remote, url=url)

    def checkout(self, branch: str) -> None:
        '''Checkout Git branch.'''
        new_branch = self.repo.create_head(branch)
        self.repo.head.reference = new_branch

    def push(
        self,
        remote: str = 'origin',
        branch: str = 'master',
    ) -> None:
        '''Push Git commits to repository.'''
        origin = self.repo.remotes[remote]
        origin.fetch()
        origin.push(branch or self.branch)

    def pull(self) -> None:
        '''Pull updates to git branch.'''
        ...

    def merge(self) -> None:
        '''Merge branch to git branch.'''
        ...

    def commit(
        self,
        basedir: str = os.getcwd(),
        filepaths: List[str] = ['*'],
        message: str = 'initial commit',
    ) -> None:
        '''Commit changes in a Git repository.'''
        for filepath in filepaths:
            self.repo.index.add(os.path.join(basedir, filepath))
        self.repo.index.commit(message)

    def tag(
        self,
        path: str,
        ref: str = 'HEAD',
        message: Optional[str] = None,
        force: bool = False,
        **kwargs: Any
    ) -> None:
        '''Tag commit message.'''
        self.repo.create_tag(
            path=path, ref=ref, message=message, force=force, **kwargs
        )
