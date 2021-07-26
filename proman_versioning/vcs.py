# -*- coding: utf-8 -*-
# copyright: (c) 2020 by Jesse Johnson.
# license: Apache 2.0, see LICENSE for more details.
'''Parse Git commit messages.'''

# import logging
import os
from typing import Any, List, Optional

from git import Repo

# from proman_versioning import exception

# from git.types import PathLike
# from transitions import Machine


class Git:
    '''Provide settings for git repositories.'''

    system_config: str = os.path.join(os.sep, 'etc', 'gitconfig')
    global_config: str = os.path.join(os.path.expanduser('~'), '.gitconfig')

    def __init__(self, repo: Repo) -> None:
        '''Initialize git object.'''
        self.repo = repo
        self.branch = 'master'
        self.hooks_dir = os.path.join(self.repo.git_dir, 'hooks')
        self.config = os.path.join(self.repo.git_dir, 'config')

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
