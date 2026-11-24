"""
test_vrtargsoolib.py

Pytest tests for vrtargsoolib: Markdown help (libvrt.mdhelp) and
epilogs in processor classes.
"""


import argparse

import pytest

from vrtargsoolib import BasicProcessor


class MarkdownProcessor(BasicProcessor):

    """Processor with Markdown help and arguments with defaults."""

    DESCRIPTION = 'Do it.\n\n::: long\nIn detail.\n:::'
    EPILOG = '::: long\n## Examples\n\n    prog --max=3\n:::'
    ARGSPECS = [
        ('--max=num:int=100',
         '''maximum value

            ::: long
            More on maximum.
            :::'''),
        ('--tag=str="<s>%"', 'tag'),
        ('--quote=str="`x"', 'quote'),
        ('--empty=str=""', 'empty'),
    ]

    class OPTIONS(BasicProcessor.OPTIONS):
        markdown_help = True


class PlainProcessor(BasicProcessor):

    """Processor without Markdown help, with an epilog."""

    DESCRIPTION = 'Do it.'
    EPILOG = 'Epilog.'
    ARGSPECS = [
        ('--max=num:int=100', 'maximum value'),
    ]

    class OPTIONS(BasicProcessor.OPTIONS):
        markdown_help = False


@pytest.fixture(autouse=True)
def no_styles(monkeypatch: pytest.MonkeyPatch):
    """Disable styling and fix the width of help output."""
    monkeypatch.setenv('PYTHON_COLORS', '0')
    monkeypatch.setenv('COLUMNS', '80')


def get_parser(cls: type[BasicProcessor]) -> argparse.ArgumentParser:
    """Return the argument parser of processor class `cls`."""
    proc = cls()
    proc._get_argparser()
    parser = proc._argparser
    assert parser is not None
    parser.prog = 'prog'
    return parser


def run(capsys: pytest.CaptureFixture[str], cls: type[BasicProcessor],
        opt: str) -> str:
    """Return the output of the parser of `cls` for option `opt`."""
    with pytest.raises(SystemExit):
        get_parser(cls).parse_args([opt])
    return capsys.readouterr().out


class TestMarkdownHelp:

    """Tests for processors with Markdown help."""

    def test_short_help(self, capsys):
        """Test defaults in the short usage message."""
        out = run(capsys, MarkdownProcessor, '-h')
        assert '--help-full' in out
        assert 'In detail' not in out
        assert '  --max num    maximum value (default: 100)\n' in out
        assert 'More on maximum' not in out
        assert ':::' not in out
        assert '  --tag str    tag (default: "<s>%")\n' in out
        assert '  --quote str  quote (default: "`x")\n' in out
        assert '  --empty str  empty (default: "")\n' in out
        assert 'Examples' not in out

    def test_full_help(self, capsys):
        """Test defaults in full help."""
        out = run(capsys, MarkdownProcessor, '--help-full')
        assert 'Do it.\n\nIn detail.\n' in out
        assert ('  --max num    maximum value (default: 100)\n\n'
                '               More on maximum.\n') in out
        assert ':::' not in out
        assert 'Examples:\n\n    prog --max=3\n' in out

    def test_markdown(self, capsys):
        """Test defaults as code spans in Markdown documentation."""
        out = run(capsys, MarkdownProcessor, '--help-markdown')
        for expected in [
                '#### `--max num`\n\nmaximum value (default: `100`)\n\n'
                'More on maximum.\n',
                '#### `--tag str`\n\ntag (default: `"<s>%"`)\n',
                '#### `--quote str`\n\nquote (default: ``"`x"``)\n',
                '#### `--empty str`\n\nempty (default: `""`)\n',
        ]:
            assert expected in out
        assert '{.plain}' not in out
        assert out.endswith('\n## Examples\n\n    prog --max=3\n')


class TestPlainHelp:

    """Tests for processors without Markdown help."""

    def test_help(self, capsys):
        """Test the default and the epilog in the usage message."""
        out = run(capsys, PlainProcessor, '-h')
        assert '--help-full' not in out
        assert '  --max num   maximum value (default: 100)\n' in out
        assert out.endswith('\nEpilog.\n')
