# type: ignore
"""Test git hooks pipeline."""

from proman.versioning.grammars.conventional_commits import CommitMessageParser


def test_title_description():
    """Test title description."""
    parser = CommitMessageParser()
    parser.parse('test')
    assert parser.title['type'] is None
    assert parser.title['description'] == 'test'


def test_title():
    """Test title."""
    parser = CommitMessageParser()
    parser.parse('fix: test')
    assert parser.title['type'] == 'fix'
    assert parser.title['description'] == 'test'


def test_title_emoji():
    """Test title emoji."""
    parser = CommitMessageParser()
    parser.parse(':sparkles:: this is a feature')
    assert parser.title['type'] == 'sparkles'
    assert parser.title['scope'] is None
    assert parser.title['description'] == 'this is a feature'


def test_title_scope():
    """Test title scope."""
    parser = CommitMessageParser()
    parser.parse('feat(ui): test')
    assert parser.title['type'] == 'feat'
    assert parser.title['scope'] == 'ui'
    assert parser.title['description'] == 'test'


def test_title_breaking_change():
    """test title breaking change."""
    parser = CommitMessageParser()
    parser.parse('refactor!: test')
    assert parser.title['type'] == 'refactor'
    assert parser.title['break'] is True
    assert parser.title['description'] == 'test'


def test_title_git_merge_description():
    """Test title git merge description."""
    parser = CommitMessageParser()
    parser.parse(
        'Merge branch \'master\' of https://example.com'
    )
    assert parser.title['type'] is None
    assert parser.title['scope'] is None
    assert parser.title['description'] == (
        'Merge branch \'master\' of https://example.com'
    )
