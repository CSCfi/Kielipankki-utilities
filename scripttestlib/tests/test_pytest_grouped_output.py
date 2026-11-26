# -*- mode: Python; -*-

"""
test_pytest_grouped_output.py

pytest tests for the pytest plugin scripttestlib.pytest_grouped_output,
running pytest on small test modules with pytester.
"""


import re

import pytest

from _pytest.pytester import Pytester, RunResult


pytest_plugins = ['pytester']


# conftest.py calling the plugin hooks twice, to test that they are
# idempotent
_conftest = """
import scripttestlib.pytest_grouped_output as plugin


def pytest_addoption(parser):
    plugin.pytest_addoption(parser)
    plugin.pytest_addoption(parser)


def pytest_configure(config):
    plugin.pytest_configure(config)
    plugin.pytest_configure(config)
"""

# A test module resembling test_scripts.py with generated test functions
_test_scripts = """
import pytest


@pytest.mark.parametrize('n', range(3))
def test_scripttest_aa_yaml(n):
    pass


# A parameter id containing "::" does not start a group of its own
@pytest.mark.parametrize('n', range(3), ids=['a::b', 'c', 'd'])
def test_scripttests_scripttest_bb_yml(n):
    pass
"""

_test_other = """
def test_other():
    pass
"""

# Run test_other between the first and the other tests of
# test_scripttest_aa_yaml
_conftest_interleave = """
def pytest_collection_modifyitems(items):
    other = [item for item in items if 'test_other' in item.nodeid]
    rest = [item for item in items if item not in other]
    items[:] = rest[:1] + other + rest[1:]
"""


@pytest.fixture
def grouped_pytester(pytester: Pytester) -> Pytester:
    """pytester with conftest.py and test modules for grouped output."""
    pytester.makeconftest(_conftest)
    pytester.makepyfile(test_scripts=_test_scripts, test_other=_test_other)
    return pytester


def _run(pytester: Pytester, *args: str) -> tuple[RunResult, list[str]]:
    """Run pytest with `args`; return (result, list of output lines)."""
    result = pytester.runpytest('-p', 'no:cacheprovider', *args)
    return result, result.outlines


def _headers(lines: list[str]) -> list[str]:
    """Return the group headers in output `lines`."""
    return [mo.group(1) for line in lines
            if (mo := re.match(r'(\S+::\S+) [.]', line))]


@pytest.mark.parametrize('args, expected', [
    ([], ['test_scripts.py::aa', 'test_scripts.py::bb']),
    (['-q'], ['test_scripts.py::aa', 'test_scripts.py::bb']),
    (['--scripttest-grouped-output=full'],
     ['test_scripts.py::test_scripttest_aa_yaml',
      'test_scripts.py::test_scripttests_scripttest_bb_yml']),
    (['--scripttest-grouped-output=none'], []),
    (['-v'], []),
    (['--scripttest-grouped-modules=test_other*'],
     ['test_other.py::other']),
    (['--scripttest-grouped-modules=test_x*, test_other*'],
     ['test_other.py::other']),
])
def test_grouped_output_headers(grouped_pytester, args, expected):
    """Test the group headers written with various options."""
    result, lines = _run(grouped_pytester, *args)
    assert result.ret == 0
    assert _headers(lines) == expected


def test_grouped_output_progress(grouped_pytester):
    """Test progress info before headers and no separate module path."""
    result, lines = _run(grouped_pytester)
    assert result.ret == 0
    # test_other.py runs first (pytest collects modules in alphabetical
    # order), so a progress line precedes also the first group header
    assert (next(i for i, line in enumerate(lines)
                 if line.startswith('test_other.py '))
            < next(i for i, line in enumerate(lines)
                   if line.startswith('test_scripts.py::')))
    # The module path of a grouped module is not output on its own
    assert not any(line.startswith('test_scripts.py ') for line in lines)
    # The line preceding each group header ends in progress info
    for i, line in enumerate(lines):
        if line.startswith('test_scripts.py::'):
            assert re.search(r'\[ *\d+%\]$', lines[i - 1])


def test_grouped_output_interleaved(grouped_pytester: Pytester) -> None:
    """Test repeating the header when a group follows another module."""
    grouped_pytester.makeconftest(_conftest + _conftest_interleave)
    result, lines = _run(grouped_pytester)
    assert result.ret == 0
    assert _headers(lines) == [
        'test_scripts.py::aa', 'test_scripts.py::aa', 'test_scripts.py::bb']


def test_grouped_output_no_terminal(grouped_pytester):
    """Test that disabling the terminal reporter does not crash."""
    result, _ = _run(grouped_pytester, '-p', 'no:terminal')
    assert result.ret == 0
