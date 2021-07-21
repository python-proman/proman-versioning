# -*- coding: utf-8 -*-
# copyright: (c) 2020 by Jesse Johnson.
# license: Apache 2.0, see LICENSE for more details.
'''Test Task-Runner.'''

from invoke import task

from proman_releases import __version__

if 'dev' in __version__ or 'rc' in __version__:
    part = 'build'
else:
    part = 'patch'


@task
def build(ctx, format=None):  # type: (Context, Optional[str]) -> None
    '''Build wheel package.'''
    if format:
        ctx.run("flit build --format={}".format(format))
    else:
        ctx.run('flit build')


@task
def install(
    ctx,
    symlink=True,
    dev=False
):  # type: (Context, bool, bool) -> None
    '''Install within environment.'''
    args = []
    if symlink:
        args.append('--symlink')
    if dev:
        args.append('--python=python3')
    ctx.run("flit install {}".format(' '.join(args)))


@task
def version(
    ctx, part=part, tag=False, commit=False, message=None
):  # type: (Context, str, bool, bool, str) -> None
    '''Update project version and apply tags.'''
    args = [part]
    if tag:
        args.append('--tag')
    if commit:
        args.append('--commit')
    else:
        args.append('--dry-run')
        args.append('--allow-dirty')
        args.append('--verbose')
        print('Add "--commit" to actually bump the version.')
    if message:
        args.append("--tag-message '{}'".format(message))
    ctx.run("bumpversion {}".format(' '.join(args)))


@task
def publish(ctx):  # type: (Context) -> None
    '''Publish project distribution.'''
    ctx.run('flit publish')


@task
def clean(ctx):  # type: (Context) -> None
    '''Clean project dependencies and build.'''
    paths = ['dist', 'logs']
    paths.append('**/__pycache__')
    paths.append('**/*.pyc')
    paths.append('proman_releases.egg-info')
    for path in paths:
        ctx.run("rm -rf {}".format(path))
