# type: ignore
"""Test git hooks pipeline."""

from versioning.grammars.conventional_commits import CommitMessageParser

message = """\
fix(example): test a message

I believe that life is basically a process of growth - that we go through many
lives, choosing situations and problems that we will learn through.

Reviewed-by: Jim H. Henson Jr. <jim.henson1@email.com>
Refs #123
Fix #124
BREAKING CHANGE: This could change things
"""


def test_footer_trailer():
    """Test footer trailer."""
    parser = CommitMessageParser()
    parser.parse(message)
    assert parser.footer['trailer']['token'] == 'Reviewed-by'
    assert parser.footer['trailer']['name'] == 'Jim H. Henson Jr.'
    assert parser.footer['trailer']['email'] == 'jim.henson1@email.com'


def test_footer_issues():
    """Test footer issues."""
    parser = CommitMessageParser()
    parser.parse(message)
    assert parser.footer['issues'][0]['Refs'] == '123'
    assert parser.footer['issues'][1]['Fix'] == '124'


def test_footer_breaking_change():
    """Test footer breaking change."""
    parser = CommitMessageParser()
    parser.parse(message)
    assert parser.footer['breaking_change'] == 'This could change things'
