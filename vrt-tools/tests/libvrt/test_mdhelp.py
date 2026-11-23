"""
test_mdhelp.py

Pytest tests for libvrt.mdhelp.
"""


import argparse

import pytest

from libvrt.mdhelp import (
    DETAIL_FULL,
    DETAIL_SHORT,
    enable_markdown_help,
    format_markdown_doc,
    insert_in_first_paragraph,
    markdown_to_plain_lines,
    select_detail,
)


class TestSelectDetail:

    """Tests for select_detail."""

    TEXT = """
        Always.

        ::: long
        Long only.
        :::

        ::: short
        Short only.
        :::

        End.
        """

    def test_short(self):
        """Test selecting the short detail level."""
        assert select_detail(self.TEXT, DETAIL_SHORT) == (
            'Always.\n\nShort only.\n\nEnd.')

    def test_full(self):
        """Test selecting the full detail level."""
        assert select_detail(self.TEXT, DETAIL_FULL) == (
            'Always.\n\nLong only.\n\nEnd.')

    def test_braced_class(self):
        """Test div markers with the class in braces."""
        text = 'a\n\n::: {.long}\nb\n:::\n\nc'
        assert select_detail(text, DETAIL_SHORT) == 'a\n\nc'
        assert select_detail(text, DETAIL_FULL) == 'a\n\nb\n\nc'

    def test_spans(self):
        """Test bracketed spans."""
        text = 'a[ long]{.long}[ short]{.short} b'
        assert select_detail(text, DETAIL_SHORT) == 'a short b'
        assert select_detail(text, DETAIL_FULL) == 'a long b'

    def test_nested_divs(self):
        """Test nested divs and divs of other classes."""
        text = ('a\n::: long\nb\n::: note\nc\n:::\nd\n:::\ne\n'
                '::: note\nf\n:::')
        assert select_detail(text, DETAIL_SHORT) == (
            'a\ne\n::: note\nf\n:::')
        assert select_detail(text, DETAIL_FULL) == (
            'a\nb\n::: note\nc\n:::\nd\ne\n::: note\nf\n:::')

    def test_markers_in_code_fence(self):
        """Test that div markers in fenced code blocks are kept."""
        text = '```\n::: long\nx\n:::\n```'
        assert select_detail(text, DETAIL_SHORT) == text

    def test_indentation_normalized(self):
        """Test that indentation is normalized."""
        text = '''first
                  second'''
        assert select_detail(text, DETAIL_SHORT) == 'first\nsecond'


class TestInsertInFirstParagraph:

    """Tests for insert_in_first_paragraph."""

    def test_simple(self):
        """Test appending to the first paragraph."""
        assert insert_in_first_paragraph('a\nb\n\nc', ' (x)') == (
            'a\nb (x)\n\nc')

    def test_skip_div(self):
        """Test skipping a paragraph beginning with a div."""
        assert insert_in_first_paragraph(
            '::: long\na\n:::\n\nb', ' (x)') == '::: long\na\n:::\n\nb (x)'

    def test_div_within_paragraph(self):
        """Test inserting before a div within the paragraph."""
        assert insert_in_first_paragraph(
            'a\n::: long\nb\n:::', ' (x)') == 'a (x)\n::: long\nb\n:::'

    def test_only_div(self):
        """Test appending to text containing only a div."""
        assert insert_in_first_paragraph('::: long\na\n:::', ' (x)') == (
            '::: long\na\n:::\n\n(x)')


class TestMarkdownToPlainLines:

    """Tests for markdown_to_plain_lines."""

    def test_paragraphs_wrapped(self):
        """Test wrapping paragraphs separately."""
        assert markdown_to_plain_lines(
            'aaa bbb\nccc ddd\n\neee fff', 8) == [
                'aaa bbb', 'ccc ddd', '', 'eee fff']

    def test_list_hanging_indent(self):
        """Test list items with a hanging indent."""
        assert markdown_to_plain_lines(
            'x:\n\n- aaa bbb ccc\n- ddd\n  eee\n1. fff', 9) == [
                'x:', '', '- aaa bbb', '  ccc', '- ddd eee', '1. fff']

    def test_code_blocks(self):
        """Test that code blocks are indented and not wrapped."""
        assert markdown_to_plain_lines(
            'a\n\n```\nx  y\n```\n\n    z  w\n\nb', 80) == [
                'a', '', '    x  y', '', '    z  w', '', 'b']

    def test_heading(self):
        """Test converting a heading."""
        assert markdown_to_plain_lines('## Examples\n\na', 80) == [
            'Examples:', '', 'a']

    def test_hard_break(self):
        """Test a hard line break."""
        assert markdown_to_plain_lines('a\\\nb', 80) == ['a', 'b']

    def test_inline(self):
        """Test converting inline markup to plain text."""
        assert markdown_to_plain_lines(
            r'`<ne>` and `x` [doc](https://x.org) \*', 80) == [
                '<ne> and `x` doc <https://x.org> *']

    def test_no_break_on_hyphens(self):
        """Test that lines are not broken at hyphens."""
        assert markdown_to_plain_lines('aa --bb-cc-dd', 8) == [
            'aa', '--bb-cc-dd']


def make_parser() -> argparse.ArgumentParser:
    """Return a test ArgumentParser with Markdown help enabled."""
    parser = argparse.ArgumentParser(
        prog='prog',
        description='Do it.\n\n::: long\nIn detail.\n:::',
        epilog='::: long\n## Examples\n\nprog --foo\n:::')
    enable_markdown_help(parser)
    parser.add_argument('infile', nargs='?', metavar='file',
                        help='input file')
    parser.add_argument('--foo', '-f', metavar='x', default='d',
                        help='''foo is x (default: %(default)s)

                                ::: long
                                Foo in detail.
                                :::''')
    group = parser.add_argument_group(
        'group', 'Group.[ More on group.]{.long}')
    group.add_argument('--bar', action='store_true', help='bar')
    return parser


class TestParser:

    """Tests for a parser with Markdown help enabled."""

    def run(self, capsys: pytest.CaptureFixture[str], opt: str) -> str:
        """Return the output of the test parser for option `opt`."""
        with pytest.raises(SystemExit):
            make_parser().parse_args([opt])
        return capsys.readouterr().out

    def test_short_help(self, capsys, monkeypatch):
        """Test the short usage message (-h)."""
        monkeypatch.setenv('COLUMNS', '80')
        out = self.run(capsys, '-h')
        assert 'Do it.\n' in out
        assert 'In detail' not in out
        assert 'foo is x (default: d)\n' in out
        assert 'Foo in detail' not in out
        assert '--help-full' in out
        assert '--help-markdown' not in out
        assert 'Group.\n' in out
        assert 'Examples' not in out
        assert ' \n' not in out

    def test_full_help(self, capsys, monkeypatch):
        """Test full help (--help-full)."""
        monkeypatch.setenv('COLUMNS', '80')
        out = self.run(capsys, '--help-full')
        assert 'Do it.\n\nIn detail.\n' in out
        assert 'foo is x (default: d)\n\n' in out
        assert 'Foo in detail.' in out
        assert 'Group. More on group.\n' in out
        assert 'Examples:\n\nprog --foo\n' in out
        assert ' \n' not in out

    def test_markdown(self, capsys):
        """Test Markdown documentation (--help-markdown)."""
        out = self.run(capsys, '--help-markdown')
        assert out == format_markdown_doc(make_parser())
        assert out.startswith('# prog\n\n## Synopsis\n\n```\nprog [-h]')
        for expected in [
                '## Description\n\nDo it.\n\nIn detail.\n\n## Arguments\n',
                '### Positional arguments\n\n#### `file`\n\ninput file\n',
                '### Options\n\n#### `-h`, `--help`\n',
                ('#### `--foo x`, `-f x`\n\nfoo is x (default: d)\n\n'
                 'Foo in detail.\n'),
                '### Group\n\nGroup. More on group.\n\n#### `--bar`\n\nbar\n',
        ]:
            assert expected in out
        assert out.endswith('\n\n## Examples\n\nprog --foo\n')
        assert '--help-markdown' not in out

    def test_markdown_epilog_without_heading(self):
        """Test adding heading "Notes" for an epilog without one."""
        parser = make_parser()
        parser.epilog = 'Note.'
        assert format_markdown_doc(parser).endswith(
            '#### `--bar`\n\nbar\n\n## Notes\n\nNote.\n')
