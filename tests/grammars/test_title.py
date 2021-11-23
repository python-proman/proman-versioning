# type: ignore
"""Test git hooks pipeline."""

from proman_versioning.grammars.conventional_commits import CommitMessageParser


def test_title():
    parser = CommitMessageParser()
    parser.parse('fix: test')
    assert parser.title['type'] == 'fix'
    assert parser.title['description'] == 'test'


def test_title_scope():
    parser = CommitMessageParser()
    parser.parse('feat(ui): test')
    assert parser.title['type'] == 'feat'
    assert parser.title['scope'] == 'ui'
    assert parser.title['description'] == 'test'


def test_title_breaking_change():
    parser = CommitMessageParser()
    parser.parse('refactor!: test')
    assert parser.title['type'] == 'refactor'
    assert parser.title['break'] is True
    assert parser.title['description'] == 'test'
