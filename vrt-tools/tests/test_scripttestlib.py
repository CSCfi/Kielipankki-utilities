#! /usr/bin/env python3


"""
test_scripttestlib.py

Very basic pytest tests for scripttestlib.
"""


import itertools
import os.path

import pytest
import yaml

from scripttestlib import (collect_testcases, check_program_run,
                           expand_testcases)


# TODO: Test more scripttestlib features, also failing tests.
_testcase_files_content = [
    ('scripttest1',
     [
         {
             'name': 'Test: prog + args as a list',
             'input': {
                 'prog': 'echo',
                 'args': ['Test1', 'Test1'],
             },
             'output': {
                 'stdout': 'Test1 Test1\n',
                 'stderr': '',
                 'returncode': 0,
             },
         },
         {
             'name': 'Test: prog + args as a string',
             'input': {
                 'prog': 'echo',
                 'args': 'Test1',
             },
             'output': {
                 'stdout': 'Test1\n',
                 'stderr': '',
                 'returncode': 0,
             },
         },
         {
             'name': 'Test: cmdline',
             'input': {
                 'cmdline': 'echo Test1',
             },
             'output': {
                 'stdout': 'Test1\n',
                 'stderr': '',
                 'returncode': 0,
             },
         },
         {
             'name': 'Test: cat stdin',
             'input': {
                 'cmdline': 'cat',
                 'stdin': 'test1\ntest2\n'
             },
             'output': {
                 'stdout': 'test1\ntest2\n',
                 'stderr': '',
                 'returncode': 0,
             },
         },
         {
             'name': 'Test: cat file',
             'input': {
                 'cmdline': 'cat infile.txt',
                 'file:infile.txt': 'test1\ntest2\n'
             },
             'output': {
                 'stdout': 'test1\ntest2\n',
                 'stderr': '',
                 'returncode': 0,
             },
         },
         {
             'name': 'Test: cat non-existent file',
             'input': {
                 'cmdline': 'cat infile.txt',
             },
             'output': {
                 'stdout': '',
                 'stderr': {
                     'test': '!=',
                     'value': '',
                 },
                 'returncode': {
                     'test': '!=',
                     'value': 0,
                 },
             },
         },
         {
             'name': 'Test: copy file',
             'input': {
                 'cmdline': 'cp infile.txt outfile.txt',
                 'file:infile.txt': 'test1\ntest2\n',
             },
             'output': {
                 'stdout': '',
                 'stderr': '',
                 'file:outfile.txt': 'test1\ntest2\n',
                 'returncode': 0,
             },
         },
         {
             'name': 'Test: environment variable',
             'input': {
                 'envvars': {
                     'foo': 'bar',
                 },
                 'cmdline': 'sh -c \'echo $foo\'',
             },
             'output': {
                 'stdout': 'bar\n',
                 'stderr': '',
                 'returncode': 0,
             },
         },
         {
             'name': 'Test: multiple expected tests (list(dict): test+value)',
             'input': {
                 'cmdline': 'cat',
                 'stdin': 'test1\ntest2\n'
             },
             'output': {
                 'stdout': [
                     # Also test simple equality with a plain scalar value
                     'test1\ntest2\n',
                     {
                         'test': '!=',
                         'value': 'foo',
                     },
                     {
                         'test': 'matches',
                         'value': 'test1',
                     },
                     {
                         'test': 'matches',
                         'value': 'test2',
                     },
                 ],
                 'stderr': '',
                 'returncode': 0,
             },
         },
         {
             'name': 'Test: multiple expected tests (list(dict): test:value)',
             'input': {
                 'cmdline': 'cat',
                 'stdin': 'test1\ntest2\n'
             },
             'output': {
                 'stdout': [
                     {
                         '!=': 'foo',
                     },
                     {
                         'matches': 'test1',
                     },
                     {
                         'matches': 'test2',
                     },
                 ],
                 'stderr': '',
                 'returncode': 0,
             },
         },
         {
             'name': 'Test: multiple expected tests (dict: test:value)',
             'input': {
                 'cmdline': 'cat',
                 'stdin': 'test1\ntest2\n'
             },
             'output': {
                 'stdout': {
                     '!=': 'foo',
                     'matches': 'test1',
                 },
                 'stderr': '',
                 'returncode': 0,
             },
         },
         {
             'name': 'Test: multiple expected tests (dict: test:[values])',
             'input': {
                 'cmdline': 'cat',
                 'stdin': 'test1\ntest2\n'
             },
             'output': {
                 'stdout': {
                     '!=': 'foo',
                     'matches': [
                         'test1',
                         'test2',
                     ],
                 },
                 'stderr': '',
                 'returncode': 0,
             },
         },
         {
             'name': 'Test: matches with flags',
             'input': {
                 'cmdline': 'cat',
                 'stdin': 'test1\ntest2\n'
             },
             'output': {
                 'stdout': {
                     'not_matches': 'test1.test2',
                     'matches DOTALL': 'test1.test2',
                     'not_matches DOTALL': 'test1 . test2',
                     'matches DOTALL|VERBOSE': 'test1 . test2',
                 },
                 'stderr': '',
                 'returncode': 0,
             },
         },
         {
             'name': 'Test: matches with flags (with re. prefix)',
             'input': {
                 'cmdline': 'cat',
                 'stdin': 'test1\ntest2\n'
             },
             'output': {
                 'stdout': {
                     'not_matches': 'test1.test2',
                     'matches re.DOTALL': 'test1.test2',
                     'not_matches re.DOTALL': 'test1 . test2',
                     'matches re.DOTALL|re.VERBOSE': 'test1 . test2',
                 },
                 'stderr': '',
                 'returncode': 0,
             },
         },
         {
             'name': 'Test: matches with flags (dict with opts in test)',
             'input': {
                 'cmdline': 'cat',
                 'stdin': 'test1\ntest2\n'
             },
             'output': {
                 'stdout': [
                     {
                         'test': 'matches DOTALL',
                         'value': 'test1.test2',
                     },
                     {
                         'test': 'matches DOTALL|VERBOSE',
                         'value': 'test1 . test2',
                     },
                 ],
                 'stderr': '',
                 'returncode': 0,
             },
         },
         {
             'name': 'Test: matches with flags (explicit "opts")',
             'input': {
                 'cmdline': 'cat',
                 'stdin': 'test1\ntest2\n'
             },
             'output': {
                 'stdout': [
                     {
                         'test': 'matches',
                         'opts': 'DOTALL',
                         'value': 'test1.test2',
                     },
                     {
                         'test': 'matches',
                         'opts': 'DOTALL|VERBOSE',
                         'value': 'test1 . test2',
                     },
                 ],
                 'stderr': '',
                 'returncode': 0,
             },
         },
         {
             'name': 'Test: pipe with shell = True',
             'input': {
                 'cmdline': 'printf "test\ntest\n" | wc -l',
                 'shell': True,
             },
             'output': {
                 'stdout': '2\n',
                 'stderr': '',
                 'returncode': 0,
             },
         },
         {
             'name': 'Test: output redirection with shell = True',
             'input': {
                 'cmdline': 'printf "test\ntest\n" > test.out',
                 'shell': True,
             },
             'output': {
                 'file:test.out': 'test\ntest\n',
                 'stdout': '',
                 'stderr': '',
                 'returncode': 0,
             },
         },
         # Note that the tests do not really check whether the tests marked to
         # be skipped or xfailing really are skipped or xfail. How could that
         # be tested?
         {
             'name': 'Test: skipping test',
             'status': 'skip',
             'input': {
             },
             'output': {
             },
         },
         {
             'name': 'Test: skipping test with reason',
             'status': 'skip: Test skipping',
             'input': {
             },
             'output': {
             },
         },
         {
             'name': 'Test: conditionally skipping test (skip)',
             'status': 'skipif: sys.version_info > (2, 0)',
             'input': {
                 'cmdline': 'cat',
                 'stdin': 'test1\ntest2\n'
             },
             'output': {
             },
         },
         {
             'name': 'Test: conditionally skipping test (do not skip)',
             'status': 'skipif: sys.version_info > (4, 0)',
             'input': {
                 'cmdline': 'cat',
                 'stdin': 'test1\ntest2\n'
             },
             'output': {
             },
         },
         {
             'name': 'Test: xfailing test',
             'status': 'xfail',
             'input': {
             },
             'output': {
             },
         },
         {
             'name': 'Test: xfailing test with reason',
             'status': 'xfail: Test xfailing',
             'input': {
             },
             'output': {
             },
         },
     ]),
]

# Testcase contents in the format expected by check_program_run.
_testcases = list(*itertools.chain(
    expand_testcases(testcases) for _, testcases in _testcase_files_content))


@pytest.fixture
def testcase_files(tmpdir):
    """pytest fixture: testcase files from _testcase_files_content

    Returns a pair (testcases, testcase file name patterns).
    """
    testcases = []
    for basename, content in _testcase_files_content:
        with open(os.path.join(tmpdir, basename + '.py'), 'w') as outf:
            outf.write('testcases = ' + repr(content) + '\n')
        testcases.extend(content)
        with open(os.path.join(tmpdir, basename + '.yaml'), 'w') as outf:
            yaml.dump(content, outf)
        testcases.extend(content)
    return (testcases, ('scripttest*.yaml', 'scripttest*.py'))


def test_collect_testcases(testcase_files, tmpdir):
    """Test scripttestlib.collect_testcases."""
    testcase_contents, testcase_filespecs = testcase_files
    testcases = collect_testcases(*testcase_filespecs, basedir=str(tmpdir))
    assert len(testcases) == len(testcase_contents)
    for testcase_num, testcase in enumerate(testcases):
        # Handle xfailing and skipping tests
        try:
            testcase = testcase.values
            assert (testcase_contents[testcase_num].get('status')
                    .startswith(('skip', 'skipif', 'xfail')))
        except AttributeError:
            pass
        assert len(testcase) == 3
        assert testcase[0] == testcase_contents[testcase_num]['name']
        assert testcase[1] == testcase_contents[testcase_num]['input']
        assert testcase[2] == testcase_contents[testcase_num]['output']


@pytest.mark.parametrize("name, input, expected", _testcases)
def test_check_program_run(name, input, expected, tmpdir):
    """Test scripttestlib.check_program_run with the testcases."""
    check_program_run(name, input, expected, tmpdir=str(tmpdir))
