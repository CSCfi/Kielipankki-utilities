"""
test_mdhelp.py

Pytest tests for libvrt.mdhelp.
"""


import argparse
import io
import random
import textwrap

import pytest

from libvrt.mdhelp import (
    can_style,
    code_span,
    DETAIL_FULL,
    DETAIL_SHORT,
    enable_markdown_help,
    format_markdown_doc,
    insert_in_first_paragraph,
    markdown_to_plain_lines,
    select_detail,
    visible_len,
    wrap_text,
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

    def test_spans_in_code(self):
        """Test that spans are kept in code spans and code blocks."""
        text = ('a [b]{.long} `[c]{.short}`\n\n```\n[d]{.long}\n```\n\n'
                '    [e]{.long}\n\n[f `g`\nh]{.long} i')
        assert select_detail(text, DETAIL_SHORT) == (
            'a  `[c]{.short}`\n\n```\n[d]{.long}\n```\n\n'
            '    [e]{.long}\n\n i')
        assert select_detail(text, DETAIL_FULL) == (
            'a b `[c]{.short}`\n\n```\n[d]{.long}\n```\n\n'
            '    [e]{.long}\n\nf `g`\nh i')


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

    def test_skip_multi_paragraph_div(self):
        """Test skipping a div containing several paragraphs."""
        assert insert_in_first_paragraph(
            '::: long\na\n\nb\n:::\n\nc', ' (x)') == (
                '::: long\na\n\nb\n:::\n\nc (x)')

    def test_skip_code_blocks(self):
        """Test skipping fenced and indented code blocks."""
        assert insert_in_first_paragraph(
            '```\na\n\nb\n```\n\nc', ' (x)') == '```\na\n\nb\n```\n\nc (x)'
        assert insert_in_first_paragraph(
            '::: note\n    a\n\n    b\n:::\nc', ' (x)') == (
                '::: note\n    a\n\n    b\n:::\nc (x)')


class TestWrapText:

    """Tests for wrap_text."""

    def test_same_as_textwrap(self):
        """Test that the result is the same as with textwrap.wrap."""
        rnd = random.Random(1234)
        words = ['a', 'bb', 'ccc', 'dddd-eeee', 'f' * 15, 'g.', '--hh-ii']
        for _ in range(500):
            text = ''.join(rnd.choice(words) + rnd.choice([' ', ' ', '  '])
                           for _ in range(rnd.randint(0, 30))).strip()
            width = rnd.randint(5, 40)
            indents = rnd.choice([('', ''), ('- ', '  '), ('', '    ')])
            assert wrap_text(text, width, *indents) == textwrap.wrap(
                text, width, initial_indent=indents[0],
                subsequent_indent=indents[1], break_on_hyphens=False,
                break_long_words=False), (text, width, indents)

    def test_escapes_not_counted(self):
        """Test that escape sequences are not counted in width."""
        bold = '\x1b[1mbbb\x1b[22m'
        assert wrap_text(f'aaa {bold} ccc', 7) == [f'aaa {bold}', 'ccc']

    def test_style_over_line_break(self):
        """Test turning a style off and on at a line break."""
        text = 'aaa \x1b[4mbbb ccc\x1b[24m ddd'
        assert wrap_text(text, 9, '', '  ') == [
            'aaa \x1b[4mbbb\x1b[24m', '  \x1b[4mccc\x1b[24m ddd']

    def test_visible_len(self):
        """Test visible_len."""
        assert visible_len('a\x1b[1mb\x1b[22m\x1b[0mc') == 3


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

    def test_fenced_code_indentation(self):
        """Test keeping the indentation of lines in fenced code."""
        assert markdown_to_plain_lines(
            'a:\n\n```\nb \\\n    c\n```\n\n  ```\n  d\n    e\n  ```', 80) == [
                'a:', '', '    b \\', '        c', '', '    d', '      e']

    def test_list_item_interrupting_paragraph(self):
        """Test which list items interrupt a paragraph (as CommonMark)."""
        assert markdown_to_plain_lines(
            'a\n2. b\n\nc\n-\nd\n\ne\n1. f\n2. g\n- h\n\ni\n* j', 80) == [
                'a 2. b', '', 'c - d', '', 'e', '1. f', '2. g', '- h', '',
                'i', '* j']

    def test_plain_code_span(self):
        """Test removing backquotes from code spans with {.plain}."""
        assert markdown_to_plain_lines(
            '(default: `"*x*"`{.plain}) ``a`b``{.plain} `y` `<z>`', 80) == [
                '(default: "*x*") a`b `y` <z>']


B0, B1 = '\x1b[1m', '\x1b[22m'
U0, U1 = '\x1b[4m', '\x1b[24m'


class TestStyledLines:

    """Tests for markdown_to_plain_lines with styled=True."""

    def styled(self, text: str, width: int = 80) -> list[str]:
        """Return `text` converted to styled lines wrapped to `width`."""
        return markdown_to_plain_lines(text, width, styled=True)

    def test_inline(self):
        """Test styling inline markup and option names."""
        assert self.styled(
            '`<ne>` **b** *u* _v_ a_b_c --opt -o x-y [d](https://x.org)') == [
                f'{B0}<ne>{B1} {B0}b{B1} {U0}u{U1} {U0}v{U1} a_b_c '
                f'{B0}--opt{B1} {B0}-o{B1} x-y d <https://x.org>']

    def test_escapes_and_code_content(self):
        """Test escapes and markup characters in code spans."""
        assert self.styled(r'\*x\* `` a`b `` `*y*`') == [
            f'*x* {B0}a`b{B1} {B0}*y*{B1}']

    def test_heading(self):
        """Test styling a heading."""
        assert self.styled('## Examples') == [f'{B0}Examples:{B1}']

    def test_wrapping_ignores_escapes(self):
        """Test that wrapping ignores escape sequences."""
        assert self.styled('aaa `bbb` ccc', 7) == [f'aaa {B0}bbb{B1}', 'ccc']

    def test_code_block_not_styled(self):
        """Test that code blocks are not styled."""
        assert self.styled('a\n\n    `x` --y') == ['a', '', '    `x` --y']

    def test_plain_code_span(self):
        """Test styling a code span with {.plain} as other code spans."""
        assert self.styled('(default: `"x"`{.plain})') == [
            f'(default: {B0}"x"{B1})']


class TestCodeSpan:

    """Tests for code_span."""

    def test_simple(self):
        """Test a code span without backquotes."""
        assert code_span('a b') == '`a b`'
        assert code_span('x', plain=True) == '`x`{.plain}'

    def test_backquotes(self):
        """Test code spans with backquotes in the content."""
        assert code_span('a`b') == '``a`b``'
        assert code_span('`a``') == '``` `a`` ```'

    def test_spaces_kept(self):
        """Test that spaces at both ends of the content are kept."""
        assert code_span(' a ') == '`  a  `'
        assert code_span(' a') == '` a`'
        assert code_span('  ') == '`  `'


class TestCanStyle:

    """Tests for can_style."""

    @pytest.fixture(autouse=True)
    def clear_env(self, monkeypatch: pytest.MonkeyPatch):
        """Unset the environment variables affecting styling."""
        for var in ['PYTHON_COLORS', 'NO_COLOR', 'FORCE_COLOR', 'TERM']:
            monkeypatch.delenv(var, raising=False)

    def test_not_terminal(self):
        """Test that a non-terminal is not styled by default."""
        assert not can_style(io.StringIO())

    def test_force_color(self, monkeypatch):
        """Test FORCE_COLOR."""
        monkeypatch.setenv('FORCE_COLOR', '1')
        assert can_style(io.StringIO())

    def test_no_color_over_force_color(self, monkeypatch):
        """Test that NO_COLOR overrides FORCE_COLOR."""
        monkeypatch.setenv('FORCE_COLOR', '1')
        monkeypatch.setenv('NO_COLOR', '1')
        assert not can_style(io.StringIO())

    def test_python_colors(self, monkeypatch):
        """Test that PYTHON_COLORS overrides NO_COLOR and FORCE_COLOR."""
        monkeypatch.setenv('NO_COLOR', '1')
        monkeypatch.setenv('PYTHON_COLORS', '1')
        assert can_style(io.StringIO())
        monkeypatch.setenv('PYTHON_COLORS', '0')
        monkeypatch.setenv('FORCE_COLOR', '1')
        assert not can_style(io.StringIO())


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

    @pytest.fixture(autouse=True)
    def no_styles(self, monkeypatch: pytest.MonkeyPatch):
        """Disable styling to make the tests independent of environment."""
        monkeypatch.setenv('PYTHON_COLORS', '0')

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

    def test_full_help_styled(self, capsys, monkeypatch):
        """Test styled full help."""
        monkeypatch.setenv('COLUMNS', '80')
        monkeypatch.setenv('PYTHON_COLORS', '1')
        out = self.run(capsys, '--help-full')
        assert f'{B0}Examples:{B1}\n\nprog {B0}--foo{B1}\n' in out

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

    def test_help_only_in_full(self, capsys):
        """Test an argument whose help text is only in full help."""
        parser = make_parser()
        parser.add_argument('--baz', help='::: long\nBaz.\n:::')
        parser.add_argument('--qux', help='[Qux.]{.long}')
        with pytest.raises(SystemExit):
            parser.parse_args(['-h'])
        out = capsys.readouterr().out
        assert '  --baz BAZ\n  --qux QUX\n' in out
        assert 'Baz.' not in out
        assert '#### `--baz BAZ`\n\nBaz.\n\n#### `--qux QUX`\n\nQux.\n' in (
            format_markdown_doc(parser))
        parser.add_argument('--quux', help='::: short\nQuux.\n:::')
        assert '#### `--quux QUUX`\n\n### Group' in (
            format_markdown_doc(parser))

    def test_markdown_plain_attribute_removed(self):
        """Test removing {.plain} from code spans in Markdown output."""
        parser = make_parser()
        parser.add_argument('--baz', help='x (default: `"y"`{.plain})')
        parser.epilog = 'See `z`{.plain}.'
        out = format_markdown_doc(parser)
        assert '\n\nx (default: `"y"`)\n' in out
        assert out.endswith('\n\nSee `z`.\n')

    def test_markdown_epilog_without_heading(self):
        """Test adding heading "Notes" for an epilog without one."""
        parser = make_parser()
        parser.epilog = 'Note.'
        assert format_markdown_doc(parser).endswith(
            '#### `--bar`\n\nbar\n\n## Notes\n\nNote.\n')
