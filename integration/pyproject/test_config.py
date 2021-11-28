# -*- coding: utf-8 -*-
# copyright: (c) 2020 by Jesse Johnson.
# license: MPL-2.0, see LICENSE for more details.
# type: ignore
"""Test configuration file."""

import os

from proman_versioning import get_release_controller, get_source_tree, Version
from proman_versioning.config import GRAMMAR_PATH

pyproject_path = os.path.abspath(
    os.path.join(
        os.path.relpath(os.path.dirname(__file__)),
        'pyproject.toml',
    )
)


def test_proman_source_tree(fs):
    """Test source tree loading."""
    fs.add_real_file(pyproject_path)
    config = get_source_tree(config_files=[pyproject_path])
    assert config.version.devreleases_enabled is True
    assert config.version.prereleases_enabled is True
    assert config.version.postreleases_enabled is True
    assert config.version == Version('1.2.3')


def test_proman_release_controller(fs):
    """Test source tree loading."""
    import lark
    COMMON_PATH = os.path.join(
        os.path.dirname(lark.__file__),
        'grammars',
        'common.lark',
    )
    fs.add_real_file(COMMON_PATH)
    fs.add_real_file(GRAMMAR_PATH)

    repo_dir = os.path.abspath(
        os.path.join(
            os.path.relpath(os.path.dirname(__file__)),
            '.gittest',
        )
    )
    fs.add_real_file(pyproject_path, False)
    controller = get_release_controller(
        repo_dir=repo_dir,
        config_files=[pyproject_path],
    )
    version = controller.bump_version(
        commit=False,
        tag=False,
        tag_name='version',
        tag_message='this is a test',
        sign_tag=False,
        dry_run=True,
    )
    print(version)
