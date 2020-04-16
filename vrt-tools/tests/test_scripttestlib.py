#! /usr/bin/env python3


"""
test_scripttestlib.py

Very basic pytest tests for scripttestlib.
"""


import itertools
import os.path

from copy import deepcopy

import pytest
import yaml

from scripttestlib import (collect_testcases, check_program_run,
                           expand_testcases, dict_deep_update)


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
             'name': 'Test: environment variable with non-self reference',
             'input': {
                 'envvars': {
                     'foo': 'bar',
                     'bar': 'foo${foo}foo$$ $foo'
                 },
                 'cmdline': 'echo $bar',
                 'shell': True,
             },
             'output': {
                 'stdout': 'foobarfoo$ bar\n',
                 'stderr': '',
                 'returncode': 0,
             },
         },
         {
             # NOTE: This does not really test that the values of PATH are HOME
             # are got from the original environment, only that they are
             # non-empty. Testing difference from the original values seems
             # currently impossible: if we had 'oldpath': '$PATH', it would
             # take the new value of PATH. This is also perhaps a bit fragile,
             # as it assumes that the original values of PATH and HOME are
             # non-empty.
             'name': 'Test: environment variable with self reference',
             'input': {
                 'envvars': {
                     'PATH': '.:$PATH',
                     'HOME': 'foo${HOME}foo',
                     # This assumes that __zz__qwerty__ is has no value in the
                     # original environment
                     '__zz__qwerty__': 'x${__zz__qwerty__}x',
                 },
                 'cmdline': ('test "$PATH" != ".:" -a "$HOME" != "foofoo"'
                             ' -a "$__zz__qwerty__" = "xx"'),
                 'shell': True,
             },
             'output': {
                 'stdout': '',
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
         # Test default values
         {
             'defaults': {
                 'input': {
                    'cmdline': 'cat',
                    'shell': True,
                 },
                 'output': {
                     'stderr': '',
                     'returncode': 0,
                 },
             },
         },
         {
             'name': 'Test: default values',
             'input': {
                 'stdin': 'test\n',
             },
             'output': {
                 'stdout': 'test\n',
             },
         },
         {
             'name': 'Test: default values, with local overrides',
             'input': {
                 'cmdline': 'cat > test.out; false',
                 'stdin': 'test\n',
             },
             'output': {
                 'file:test.out': 'test\n',
                 'returncode': 1,
             },
         },
         # Change default values
         {
             'defaults': {
                 'input': {
                    'cmdline': 'cat test.in > /dev/stderr',
                 },
                 'output': {
                     'stderr': {},
                 },
             },
         },
         {
             'name': 'Test: changed default values, with local overrides',
             'input': {
                 'file:test.in': 'test\n',
             },
             'output': {
                 'stderr': 'test\n',
             },
         },
         # Clear default values
         {
             'defaults': {},
         },
         {
             'name': 'Test: try to use cleared default values',
             'status': 'xfail:Tries to use cleared default values',
             'input': {
                 'file:test.in': 'test\n',
             },
             'output': {
                 'stderr': 'test\n',
             },
         },
         # Output options
         {
             'name': 'Test: option filter-out for stdout',
             'input': {
                 'cmdline': 'printf "foo\nbar\n"',
              },
             'output': {
                 'options': {
                     'filter-out stdout': 'o',
                 },
                 'stdout': 'f\nbar\n',
                 'stderr': '',
                 'returncode': 0,
              },
         },
         {
             'name': 'Test: option filter-out for all output',
             'input': {
                 'cmdline': 'printf "foo\nbar\n" | tee /dev/stderr test.out',
                 'shell': True,
              },
             'output': {
                 'options': {
                     'filter-out': 'o',
                 },
                 'stdout': 'f\nbar\n',
                 'stderr': 'f\nbar\n',
                 'file:test.out': 'f\nbar\n',
                 'returncode': 0,
              },
         },
         {
             'name': 'Test: option filter-out for named output file',
             'input': {
                 'cmdline': 'printf "foo\nbar\n" > test.out',
                 'shell': True,
              },
             'output': {
                 'options': {
                     'filter-out file:test.out': 'o',
                 },
                 'stdout': '',
                 'stderr': '',
                 'file:test.out': 'f\nbar\n',
                 'returncode': 0,
              },
         },
         {
             'name': 'Test: option filter-out with a regexp',
             'input': {
                 'cmdline': 'printf "aabb\nccdd\neeff\n"',
                 'shell': True,
              },
             'output': {
                 'options': {
                     'filter-out': 'c.*\n',
                 },
                 'stdout': 'aabb\neeff\n',
                 'stderr': '',
                 'returncode': 0,
              },
         },
         {
             'name': 'Test: multiple filter-out options',
             'input': {
                 'cmdline': 'printf "foo\nbar\nbaz\n" | tee /dev/stderr test.out',
                 'shell': True,
              },
             'output': {
                 'options': {
                     'filter-out': 'b',
                     'filter-out stdout': 'o',
                     'filter-out stderr': 'a',
                     'filter-out file:test.out': 'foo\n',
                 },
                 'stdout': 'f\nar\naz\n',
                 'stderr': 'foo\nr\nz\n',
                 'file:test.out': 'ar\naz\n',
                 'returncode': 0,
              },
         },
         {
             'name': 'Test: option filter-out with a list value',
             'input': {
                 'cmdline': 'printf "foo\nbar\nbaz\n"',
              },
             'output': {
                 'options': {
                     'filter-out': [
                         'o',
                         'b',
                     ],
                 },
                 'stdout': 'f\nar\naz\n',
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
_testcases = expand_testcases(_testcase_files_content)


@pytest.fixture
def testcase_files(tmpdir):
    """pytest fixture: testcase files from _testcase_files_content

    Returns a pair (testcases, testcase file name patterns).
    """
    testcases = []
    fname_patts = []
    for basename, content in _testcase_files_content:
        for ext, write_fn in (
            ('.py', lambda outf, content: (
                outf.write('testcases = ' + repr(content) + '\n'))),
            ('.yaml', lambda outf, content: yaml.dump(content, outf)),
            ):
            with open(os.path.join(tmpdir, basename + ext), 'w') as outf:
                write_fn(outf, content)
            testcases.append((basename + ext, content))
            # print(basename + ext, content)
            fname_patts.append('scripttest*' + ext)
    return (testcases, fname_patts)


def test_collect_testcases(testcase_files, tmpdir):
    """Test scripttestlib.collect_testcases."""
    fname_testcase_contents, testcase_filespecs = testcase_files
    testcases = collect_testcases(*testcase_filespecs, basedir=str(tmpdir))
    assert len(testcases) == sum(
        len([tc for tc in tc_conts if 'defaults' not in tc])
        for _, tc_conts in fname_testcase_contents)
    testcase_num = 0
    # print(testcases)
    for fname, testcase_contents in fname_testcase_contents:
        # print(fname, testcase_contents)
        default_values = {}
        for testcase_cont_num, testcase_cont in enumerate(testcase_contents):
            if 'defaults' in testcase_cont:
                assert all(key in ['input', 'output', 'status']
                           for key in testcase_cont['defaults'])
                # deepcopy is needed because otherwise default_values may
                # reference parts of testcase_cont['defaults'], and when
                # default_values changes, testcase_cont['defaults'] may also
                # change, which may result in incorrect results for the second
                # testcase file. An alternative would be to use deepcopy in the
                # testcase_files fixture to make a separate copy the whole
                # content for both files.
                default_values = dict_deep_update(
                    default_values, deepcopy(testcase_cont['defaults']))
                continue
            testcase = testcases[testcase_num]
            # Handle xfailing and skipping tests
            try:
                testcase = testcase.values
                assert (testcase_cont.get('status')
                        .startswith(('skip', 'skipif', 'xfail')))
            except AttributeError:
                pass
            assert len(testcase) == 3
            assert testcase[0] == '{} {:d}: {}'.format(
                fname, testcase_cont_num + 1, testcase_cont['name'])
            assert testcase[1] == dict_deep_update(
                dict(default_values.get('input', {})), testcase_cont['input'])
            assert testcase[2] == dict_deep_update(
                dict(default_values.get('output', {})), testcase_cont['output'])
            testcase_num += 1


def test_dict_deep_update():
    """Test dict_deep_update."""

    def check(val1, val2, result):
        assert dict_deep_update(deepcopy(val1), val2) == result

    da1 = {'a': 1}
    db2 = {'b': 2}
    dbc3 = {'b': {'c': 3}}
    dbc4 = {'b': {'c': 4}}
    dbd5 = {'b': {'d': 5}}
    dbe = {'b': {}}
    check(None, None, None)
    check(None, {}, {})
    check({}, None, None)
    check(1, {}, {})
    check({}, da1, da1)
    check(da1, 1, 1)
    check(da1, db2, {'a': 1, 'b': 2})
    check(db2, dbc3, dbc3)
    check(dbc3, db2, db2)
    check(da1, dbc3, {'a': 1, 'b': {'c': 3}})
    check(dbc3, da1, {'a': 1, 'b': {'c': 3}})
    check(dbc3, dbc4, dbc4)
    check(dbc3, dbd5, {'b': {'c': 3, 'd': 5}})
    check(dbd5, dbe, dbe)


def test_empty_values(tmpdir):
    """Test with empty values for some required items."""
    with pytest.raises(ValueError) as e_info:
        check_program_run('Empty cmdline',
                          {'name': 'Empty cmdline',
                           'input': {'cmdline': ''}}, {}, tmpdir=str(tmpdir))
    with pytest.raises(ValueError) as e_info:
        check_program_run('Empty input info',
                          {'name': 'Empty input info',
                           'input': {}}, {}, tmpdir=str(tmpdir))
    with pytest.raises(ValueError) as e_info:
        check_program_run('Empty input info',
                          {'name': 'Empty prog',
                           'input': {'prog': ''}}, {}, tmpdir=str(tmpdir))
    with pytest.raises(ValueError) as e_info:
        check_program_run('Empty input args',
                          {'name': 'Empty prog',
                           'input': {'args': []}}, {}, tmpdir=str(tmpdir))


@pytest.mark.parametrize("name, input, expected", _testcases)
def test_check_program_run(name, input, expected, tmpdir):
    """Test scripttestlib.check_program_run with the testcases."""
    check_program_run(name, input, expected, tmpdir=str(tmpdir))
