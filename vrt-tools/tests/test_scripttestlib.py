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

from tests.scripttestlib import (
    collect_testcases, check_program_run, expand_testcases,
    dict_deep_update, make_param_id)


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
             'name': 'Test: test with expected dict with only "value"',
             'input': {
                 'cmdline': 'cat',
                 'stdin': 'test1\ntest2\n'
             },
             'output': {
                 'stdout': {
                     'value': 'test1\ntest2\n',
                 },
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
                         'test': 'regex',
                         'value': 'test1',
                     },
                     {
                         'test': 'regex',
                         'value': 'test2',
                     },
                 ],
                 'stderr': '',
                 'returncode': 0,
             },
         },
         {
             'name': 'Test: multiple expected tests with names',
             'input': {
                 'cmdline': 'cat',
                 'stdin': 'test1\ntest2\n'
             },
             'output': {
                 'stdout': [
                     {
                         'name': 'not foo',
                         'test': '!=',
                         'value': 'foo',
                     },
                     {
                         'name': 'regexp match 1',
                         'test': 'regex',
                         'value': 'test1',
                     },
                     {
                         'name': 'regexp match 2',
                         'test': 'regex',
                         'value': 'test2',
                     },
                 ],
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
                         'regex': 'test1',
                     },
                     {
                         'regex': 'test2',
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
                     'regex': 'test1',
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
                     'regex': [
                         'test1',
                         'test2',
                     ],
                 },
                 'stderr': '',
                 'returncode': 0,
             },
         },
         {
             'name': 'Test: regex with flags',
             'input': {
                 'cmdline': 'cat',
                 'stdin': 'test1\ntest2\n'
             },
             'output': {
                 'stdout': {
                     'not-regex': 'test1.test2',
                     'regex DOTALL': 'test1.test2',
                     'not-regex DOTALL': 'test1 . test2',
                     'regex DOTALL|VERBOSE': 'test1 . test2',
                 },
                 'stderr': '',
                 'returncode': 0,
             },
         },
         {
             'name': 'Test: regex with flags (with re. prefix)',
             'input': {
                 'cmdline': 'cat',
                 'stdin': 'test1\ntest2\n'
             },
             'output': {
                 'stdout': {
                     'not-regex': 'test1.test2',
                     'regex re.DOTALL': 'test1.test2',
                     'not-regex re.DOTALL': 'test1 . test2',
                     'regex re.DOTALL|re.VERBOSE': 'test1 . test2',
                 },
                 'stderr': '',
                 'returncode': 0,
             },
         },
         {
             'name': 'Test: regex with flags (dict with opts in test)',
             'input': {
                 'cmdline': 'cat',
                 'stdin': 'test1\ntest2\n'
             },
             'output': {
                 'stdout': [
                     {
                         'test': 'regex DOTALL',
                         'value': 'test1.test2',
                     },
                     {
                         'test': 'regex DOTALL|VERBOSE',
                         'value': 'test1 . test2',
                     },
                 ],
                 'stderr': '',
                 'returncode': 0,
             },
         },
         {
             'name': 'Test: regex with flags (explicit "reflags")',
             'input': {
                 'cmdline': 'cat',
                 'stdin': 'test1\ntest2\n'
             },
             'output': {
                 'stdout': [
                     {
                         'test': 'regex',
                         'reflags': 'DOTALL',
                         'value': 'test1.test2',
                     },
                     {
                         'test': 'regex',
                         'reflags': 'DOTALL|VERBOSE',
                         'value': 'test1 . test2',
                     },
                 ],
                 'stderr': '',
                 'returncode': 0,
             },
         },
         {
             'name': 'Test: test <, >, <=, >=',
             'input': {
                 'cmdline': 'cat',
                 'stdin': 'test1\ntest2\n'
             },
             'output': {
                 'stdout': [
                     {
                         'test': '>',
                         'value': 'a',
                     },
                     {
                         'test': '>=',
                         'value': 'a',
                     },
                     {
                         'test': '<',
                         'value': 'z',
                     },
                     {
                         'test': '<=',
                         'value': 'z',
                     },
                 ],
                 'stderr': '',
                 'returncode': 0,
             },
         },
         {
             'name': 'Test: test in, not-in, contains, not-contains',
             'input': {
                 'cmdline': 'cat',
                 'stdin': 'test1\ntest2\n'
             },
             'output': {
                 'stdout': [
                     # "in", "not-in" with list value
                     {
                         'name': '"in" with list value',
                         'test': 'in',
                         'value': [
                            'a',
                            'test1\ntest2\n',
                         ],
                     },
                     {
                         'name': '"not-in" with list value',
                         'test': 'not-in',
                         'value': [
                            'test0\ntest1\ntest2\n',
                            'b',
                         ],
                     },
                     # "in", "not-in" with string value
                     {
                         'name': '"in" with string value',
                         'test': 'in',
                         'value': 'test0\ntest1\ntest2\n',
                     },
                     {
                         'name': '"not-in" with string value',
                         'test': 'not-in',
                         'value': 'test0\ntest2\n',
                     },
                     # "in", "not-in" with test name as key, str value
                     {
                         'in': 'test0\ntest1\ntest2\n',
                         'not-in': 'test0\ntest2\n',
                     },
                     # "in", "not-in" with test name as key, list value
                     {
                         'in': [
                             [
                                 'a',
                                 'test1\ntest2\n',
                             ],
                             'test0\ntest1\ntest2\n',
                         ],
                     },
                     {
                         'not-in': [[
                            'test0\ntest1\ntest2\n',
                            'b',
                         ]],
                     },
                     # "contains", "not-contains"
                     {
                         'name': 'contains',
                         'test': 'contains',
                         'value': 'test',
                     },
                     {
                         'name': 'not-contains',
                         'test': 'not-contains',
                         'value': 'test3',
                     },
                 ],
                 'stderr': '',
                 'returncode': 0,
             },
         },
         {
             'name': 'Test: test with alternative test names',
             'input': {
                 'cmdline': 'cat',
                 'stdin': 'test1\ntest2\n'
             },
             'output': {
                 'stdout': [
                     {
                         'test': 'not-equal',
                         'value': '',
                     },
                     {
                         'test': 'greater',
                         'value': 'a',
                     },
                     {
                         'test': 'greater-equal',
                         'value': 'a',
                     },
                     {
                         'test': 'less',
                         'value': 'z',
                     },
                     {
                         'test': 'less-equal',
                         'value': 'z',
                     },
                     {
                         'test': 'matches',
                         'value': 'test1',
                     },
                     {
                         'test': 'not-matches',
                         'value': 'foo',
                     },
                 ],
                 'stderr': '',
                 'returncode': 0,
             },
         },
         {
             'name': 'Test: test "python"',
             'input': {
                 'cmdline': 'cat',
                 'stdin': 'test1\ntest2\n',
             },
             'output': {
                 'stdout': [
                     {'python': 'return value == "test1\\ntest2\\n"'},
                     # Test availability of module re
                     {
                         'name': 'availability of module re',
                         'test': 'python',
                         'value': 'return re.search(r".*1", value) is not None',
                     },
                     {
                         'test': 'python',
                         'value': 'return "test3" not in value',
                     },
                     {
                         'name': 'multi-line Python function',
                         'test': 'python',
                         'value': 's = "test3"\nreturn s not in value',
                     },
                 ],
             },
         },
         {
             'name': 'Test: test "shell"',
             'input': {
                 'cmdline': 'cat in.txt | tee out.txt',
                 'shell': True,
                 'file:in.txt': 'test1\ntest2\n',
                 'envvars': {
                     'foo': 'bar',
                 },
             },
             'output': {
                 'stdout': [
                     {'shell': 'test "x" = "x"'},
                     {'shell': 'diff - in.txt'},
                     # Test that input and output files are accessible
                     {
                         'name': 'input and output files accessible',
                         'test': 'shell',
                         'value': 'diff in.txt out.txt',
                     },
                     # Test environment variables
                     {
                         'name': 'environment variables',
                         'test': 'shell',
                         'value': 'test "$foo" = "bar"',
                     },
                     # Test $(...)
                     {
                         'name': '$(...)',
                         'test': 'shell',
                         'value': 'test "$(wc -l < out.txt)" = 2',
                     },
                 ],
                 # Test that file content works
                 'file:out.txt': [
                     {
                         'name': 'file content',
                         'test': 'shell',
                         'value': 'diff - in.txt',
                     },
                 ],
             },
         },
         {
             'name': 'Test: expected value from file',
             'input': {
                 'cmdline': 'cat in.txt | tee out.txt',
                 'shell': True,
                 'file:in.txt': 'test1\ntest2\n',
             },
             'output': {
                 'stdout': [
                     {'value': {'file': 'in.txt'}},
                     {'value': {'file': 'out.txt'}},
                 ],
                 'file:out.txt': [
                     {'value': {'file': 'in.txt'}},
                     {'==': {'file': 'in.txt'}},
                     # Test transformation with value from file
                     {
                         'name': 'transformation with value from file',
                         'test': 'contains',
                         'value': {'file': 'in.txt'},
                         'transform-actual': {
                             'prepend': 'test0\n',
                         },
                     },
                     {
                         'test': 'in',
                         'value': {'file': 'in.txt'},
                         'transform-expected': {
                             'prepend': 'test0\n',
                         },
                     },
                     # Same with "transform" instead of
                     # "transform-expected"
                     {
                         'test': 'in',
                         'value': {'file': 'in.txt'},
                         'transform': {
                             'prepend': 'test0\n',
                         },
                     },
                 ],
             },
         },
         {
             'name': 'Test: expected value generated with Python code',
             'input': {
                 'cmdline': 'cat in.txt | tee out.txt',
                 'shell': True,
                 'file:in.txt': 'test1\ntest2\n',
             },
             'output': {
                 'stdout': [
                     {'value': {'python': 'return "test1\\ntest2\\n"'}},
                 ],
                 'file:out.txt': [
                     {'value': {'python': 'return "test1\\ntest2\\n"'}},
                     {'==': {'python': 'return "test1\\ntest2\\n"'}},
                     {'!=': {'python': 'return "test1\\n"'}},
                     {
                         'name': 'multi-line Python function',
                         'test': '!=',
                         'value': {'python': 's = "test1"\nreturn s'},
                     },
                     # Test transformation with value generated with Python
                     {
                         'name': 'transformation with value generated with Python',
                         'test': 'contains',
                         'value': {'python': 'return "test1\\ntest2\\n"'},
                         'transform-actual': {
                             'prepend': 'test0\n',
                         },
                     },
                     {
                         'test': 'in',
                         'value': {'python': 'return "test1\\ntest2\\n"'},
                         'transform-expected': {
                             'prepend': 'test0\n',
                         },
                     },
                 ],
             },
         },
         {
             'name': 'Test: expected value generated with shell command',
             'input': {
                 'cmdline': 'cat in.txt | tee out.txt',
                 'shell': True,
                 'file:in.txt': 'test1\ntest2\n',
                 'envvars': {
                     'foo': 'test1',
                 },
             },
             'output': {
                 'stdout': [
                     {'value': {'shell': 'echo test1; echo test2'}},
                 ],
                 'file:out.txt': [
                     {'value': {'shell': 'echo test1; echo test2'}},
                     {'==': {'shell': 'echo test1; echo test2'}},
                     {'!=': {'shell': 'echo test1'}},
                     # Environment variable access
                     {
                         'name': 'environment variable access',
                         'value': {'shell': 'echo "$foo"; echo test2'},
                     },
                     # Test transformation with value generated with shell
                     {
                         'name': 'transformation with value generated with shell',
                         'test': 'contains',
                         'value': {'shell': 'echo test1; echo test2'},
                         'transform-actual': {
                             'prepend': 'test0\n',
                         },
                     },
                     {
                         'test': 'in',
                         'value': {'shell': 'echo test1; echo test2'},
                         'transform-expected': {
                             'prepend': 'test0\n',
                         },
                     },
                 ],
             },
         },
         {
             'name': 'Test: input value generated with Python code',
             'input': {
                 'cmdline': 'cat in1.txt in2.txt',
                 'shell': True,
                 'file:in1.txt': {
                     'value': {'python': 'return "test1\\ntest2\\n"'},
                 },
                 # With transformation
                 'file:in2.txt': {
                     'value': {'python': 'return "test1\\ntest2\\n"'},
                     'transform': {
                         'replace': '/[0-9]/*/',
                     },
                 },
             },
             'output': {
                 'stdout': 'test1\ntest2\ntest*\ntest*\n',
             },
         },
         {
             'name': 'Test: input value generated with shell command',
             'input': {
                 'cmdline': 'cat in1.txt in2.txt',
                 'shell': True,
                 'file:in1.txt': {
                     'value': {'shell': 'echo test1; echo test2'},
                 },
                 # With transformation
                 'file:in2.txt': {
                     'value': {'shell': 'echo test1; echo test2'},
                     'transform': {
                         'replace': '/[0-9]/*/',
                     },
                 },
             },
             'output': {
                 'stdout': 'test1\ntest2\ntest*\ntest*\n',
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
         {
             'name': 'Test: (non-)existence of files',
             'input': {
                 'cmdline': 'printf "test\ntest\n" > test.out',
                 'shell': True,
             },
             'output': {
                 'stdout': '',
                 'stderr': '',
                 'returncode': 0,
                 'file:test.out': {
                     '!=': None,
                 },
                 'file:test2.out': None,
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
         # Change default values for input only
         {
             'defaults': {
                 'input': {
                    'file:test.in': 'test2\n',
                 },
             },
         },
         {
             'name': 'Test: changed only input defaults',
             'output': {
                 'stderr': 'test2\n',
             },
         },
         # Change default values for output only
         {
             'defaults': {
                 'output': {
                    'stderr': 'test3\n',
                 },
             },
         },
         {
             'name': 'Test: changed only output defaults',
             'input': {
                 'file:test.in': 'test3\n',
             },
         },
         {
             'name': 'Test: override default with a dict value',
             'input': {
                 'file:test.in': 'test4\n',
             },
             'output': {
                 'stderr': 'test4\n',
             },
         },
         # Default value with a dict and local override
         {
             'defaults': {
                 'output': {
                    'stderr': {
                        'value': 'test5\n',
                    },
                 },
             },
         },
         {
             'name': 'Test: default output with a dict value',
             'input': {
                 'file:test.in': 'test5\n',
             },
         },
         {
             'defaults': {
                 'output': {
                    'stderr': {
                        'value': 'test6\n',
                    },
                 },
             },
         },
         {
             'name': 'Test: default output with a changed dict value',
             'input': {
                 'file:test.in': 'test6\n',
             },
         },
         {
             'name': 'Test: overriding default output with a dict value',
             'input': {
                 'file:test.in': 'test7\n',
             },
             'output': {
                 'stderr': {
                     'value': 'test7\n',
                 },
             },
         },
         {
             'name': 'Test: overriding default output with a scalar value',
             'input': {
                 'file:test.in': 'test8\n',
             },
             'output': {
                 'stderr': 'test8\n',
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
         # Input and output transformation options
         {
             'name': 'Test: transform-actual filter-out for stdout',
             'input': {
                 'cmdline': 'printf "foo\nbar\n"',
              },
             'output': {
                 'stdout': {
                     'value': 'f\nbar\n',
                     'transform-actual': {
                         'filter-out': 'o',
                     },
                 },
                 'stderr': '',
                 'returncode': 0,
              },
         },
         {
             'name': 'Test: transform-actual filter-out for all output',
             'input': {
                 'cmdline': 'printf "foo\nbar\n" | tee /dev/stderr test.out',
                 'shell': True,
              },
             'output': {
                 'transform-actual': {
                     'filter-out': 'o',
                 },
                 'stdout': 'f\nbar\n',
                 'stderr': 'f\nbar\n',
                 'file:test.out': 'f\nbar\n',
                 'returncode': 0,
              },
         },
         {
             'name': 'Test: transform-actual filter-out for named output file',
             'input': {
                 'cmdline': 'printf "foo\nbar\n" > test.out',
                 'shell': True,
              },
             'output': {
                 'stdout': '',
                 'stderr': '',
                 'file:test.out': {
                     'value': 'f\nbar\n',
                     'transform-actual': {
                         'filter-out': 'o',
                     },
                 },
                 'returncode': 0,
              },
         },
         {
             'name': 'Test: transform-actual filter-out with a regexp',
             'input': {
                 'cmdline': 'printf "aabb\nccdd\neeff\n"',
                 'shell': True,
              },
             'output': {
                 'transform-actual': {
                     'filter-out': 'c.*\n',
                 },
                 'stdout': 'aabb\neeff\n',
                 'stderr': '',
                 'returncode': 0,
              },
         },
         {
             'name': 'Test: multiple transform-actual filter-out transformations',
             'input': {
                 'cmdline': 'printf "foo\nbar\nbaz\n" | tee /dev/stderr test.out',
                 'shell': True,
              },
             'output': {
                 'transform-actual': {
                     'filter-out': 'o',
                 },
                 'stdout': {
                     'value': 'f\nar\naz\n',
                     'transform-actual': {
                         'filter-out': 'b',
                     },
                 },
                 'stderr': {
                     'value': 'f\nbr\nbz\n',
                     'transform-actual': {
                         'filter-out': 'a',
                     },
                 },
                 'file:test.out':  {
                     'value': 'f\nbar\nbaz\n',
                     'transform-actual': {
                         # "foo" is not found, as "o" is filtered out first
                         'filter-out': 'foo\n',
                     },
                 },
                 'returncode': 0,
              },
         },
         {
             'name': 'Test: transform-actual filter-out with a list value',
             'input': {
                 'cmdline': 'printf "foo\nbar\nbaz\n"',
              },
             'output': {
                 'transform-actual': {
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
         {
             'name': 'Test: append and prepend to stdin',
             'input': {
                 'cmdline': 'cat',
                 'stdin': {
                     'value': 'bar\n',
                     'transform': {
                         'prepend': 'foo\n',
                         'append': 'baz\n',
                     },
                 },
             },
             'output': {
                 'stdout': 'foo\nbar\nbaz\n',
                 'stderr': '',
                 'returncode': 0,
             },
         },
         {
             'name': 'Test: append and prepend to input file',
             'input': {
                 'cmdline': 'cat file.in',
                 'file:file.in': {
                     'value': 'bar\n',
                     'transform': {
                         'prepend': 'foo\n',
                         'append': 'baz\n',
                     },
                 },
             },
             'output': {
                 'stdout': 'foo\nbar\nbaz\n',
                 'stderr': '',
                 'returncode': 0,
             },
         },
         {
             'name': 'Test: append and prepend to stdout',
             'input': {
                 'cmdline': 'cat',
                 'stdin': 'foo\nbar\nbaz\n'
             },
             'output': {
                 'stdout': [
                     {
                         'value': 'bar\n',
                         'transform-expected': {
                             'prepend': 'foo\n',
                             'append': 'baz\n',
                         },
                     },
                     # The same with "transform" instead of
                     # "transform-expected"
                     {
                         'value': 'bar\n',
                         'transform': {
                             'prepend': 'foo\n',
                             'append': 'baz\n',
                         },
                     },
                 ],
                 'stderr': '',
                 'returncode': 0,
             },
         },
         {
             'name': 'Test: append and prepend to output file',
             'input': {
                 'cmdline': 'cat > file.out',
                 'shell': True,
                 'stdin': 'foo\nbar\nbaz\n'
             },
             'output': {
                 'file:file.out': {
                     'value': 'bar\n',
                     'transform-expected': {
                         'prepend': 'foo\n',
                         'append': 'baz\n',
                     },
                 },
                 'stderr': '',
                 'returncode': 0,
             },
         },
         {
             'name': 'Test: completely replace output file content',
             'input': {
                 'cmdline': 'cat > file.out',
                 'shell': True,
                 'stdin': 'foo\nbar\nbaz\n'
             },
             'output': {
                 'file:file.out': {
                     'value': 'bar\n',
                     'transform-expected': {
                         'set-value': 'foo\nbar\nbaz\n',
                     },
                 },
             },
         },
         {
             'name': 'Test: completely replace output file content (implicit set-value)',
             'input': {
                 'cmdline': 'cat > file.out',
                 'shell': True,
                 'stdin': 'foo\nbar\nbaz\n'
             },
             'output': {
                 'file:file.out': {
                     'value': 'bar\n',
                     'transform-expected': 'foo\nbar\nbaz\n',
                 },
             },
         },
         {
             'name': 'Test: transform with implicit set-value in list',
             'input': {
                 'cmdline': 'cat foo',
             },
             'output': {
                 'stdout': '',
                 'stderr': {
                     'value': '',
                     'transform-expected': [
                         'cat: foo: ',
                         {'append': 'No such file or directory\n'},
                     ],
                 },
                 'returncode': {
                     'value': 0,
                     'transform-expected': 1,
                 },
             },
         },
         {
             'name': 'Test: transform with implicit set-value None',
             'input': {
                 'cmdline': 'cat foo bar',
                 'file:foo': {
                     'value': 'foo\n',
                     'transform': [
                         None,
                     ],
                 },
                 'file:bar': {
                     'value': '',
                     'transform': 'bar\n',
                 },
             },
             'output': {
                 'stdout': {
                     'value': 'foo\n',
                     'transform-expected': 'bar\n',
                 },
                 'stderr': {
                     'value': '',
                     'transform-expected': [
                         'cat: foo: ',
                         {'append': 'No such file or directory\n'},
                     ],
                 },
                 'file:foo': {
                     'value': 'foo\n',
                     'transform-expected': [
                         None,
                     ],
                 },
                 'file:bar': {
                     'value': 'baz\n',
                     'transform-expected': 'bar\n',
                 },
                 'returncode': {
                     'value': 0,
                     'transform-expected': 1,
                 },
             },
         },
         {
             'name': 'Test: transform stdin with shell (+ append)',
             'input': {
                 'cmdline': 'cat',
                 'stdin': {
                     'value': 'foo\nbar\n',
                     'transform': {
                         'shell': 'head -1 | tr -d "fb"',
                         'append': 'baz\n',
                     },
                 },
             },
             'output': {
                 'stdout': 'oo\nbaz\n',
                 'stderr': '',
                 'returncode': 0,
             },
         },
         {
             'name': 'Test: transform stdout with shell (+ append)',
             'input': {
                 'cmdline': 'cat',
                 'stdin': 'oo\nbaz\n'
             },
             'output': {
                 'stdout': {
                     'value': 'foo\nbar\n',
                     'transform-expected': [
                         {'shell': 'head -1 | tr -d "fb"'},
                         {'append': 'baz\n'},
                     ],
                 },
                 'stderr': '',
                 'returncode': 0,
             },
         },
         {
             'name': 'Test: transform actual stdout with shell command referring to input or output file',
             'input': {
                 'cmdline': 'cat in.txt | tee out.txt',
                 'shell': True,
                 'file:in.txt': '1\n2\n3\n',
             },
             'output': {
                 'stdout': [
                     '1\n2\n3\n',
                     {
                         'test': '==',
                         'value': '',
                         'transform-actual': {'shell': 'diff - in.txt'},
                     },
                     {
                         'test': '==',
                         'value': '',
                         'transform-actual': {'shell': 'diff - out.txt'},
                     },
                 ],
                 'file:out.txt': [
                     '1\n2\n3\n',
                     {
                         'test': '==',
                         'value': '',
                         'transform-actual': {'shell': 'diff - in.txt'},
                     },
                 ],
                 'stderr': '',
                 'returncode': 0,
             },
         },
         {
             'name': 'Test: transform actual stdout with shell command referring to environment',
             'input': {
                 'cmdline': 'echo "$foo"',
                 'shell': True,
                 'envvars': {
                     'foo': 'bar',
                 },
             },
             'output': {
                 'stdout': [
                     'bar\n',
                     {
                         'test': '==',
                         'value': 'barbar\n',
                         'transform-actual': {'shell': 'echo "$foo$foo"'},
                     },
                 ],
                 'stderr': '',
                 'returncode': 0,
             },
         },
         {
             'name': 'Test: transform stdin with Python (+ append)',
             'input': {
                 'cmdline': 'cat',
                 'stdin': {
                     'value': 'foo\nbar\n',
                     'transform': {
                         'python': ('return re.sub(r"\\n.*", "\\n", value,'
                                    ' flags=re.DOTALL)[1:]'),
                         'append': 'baz\n',
                     },
                 },
             },
             'output': {
                 'stdout': 'oo\nbaz\n',
                 'stderr': '',
                 'returncode': 0,
             },
         },
         {
             'name': 'Test: transform stdout with shell (+ append)',
             'input': {
                 'cmdline': 'cat',
                 'stdin': 'oo\nbaz\n'
             },
             'output': {
                 'stdout': {
                     'value': 'foo\nbar\n',
                     'transform-expected': {
                         'python': (
                             'return re.sub(r"\\n.*", "\\n", value,'
                                            ' flags=re.DOTALL)[1:]\n'),
                         'append': 'baz\n',
                     },
                 },
                 'stderr': '',
                 'returncode': 0,
             },
         },
         {
             'name': 'Test: transform cmdline',
             'input': {
                 'cmdline': {
                     'value': 'echo "foobar"',
                     'transform': {
                         'replace': '/foo/bar/',
                     },
                 },
             },
             'output': {
                 'stdout': 'barbar\n',
             },
         },
         {
             'name': 'Test: replace string in stdin',
             'input': {
                 'cmdline': 'cat',
                 'stdin': {
                     'value': 'foo\nbar\nbaz\n',
                     'transform': {
                         'replace': {
                             'str': 'b',
                             'with': 'x',
                         },
                     },
                 },
             },
             'output': {
                 'stdout': 'foo\nxar\nxaz\n',
             },
         },
         {
             'name': 'Test: replace string in stdin, without "with"',
             'input': {
                 'cmdline': 'cat',
                 'stdin': {
                     'value': 'foo\nbar\nbaz\n',
                     'transform': {
                         'replace': {
                             'str': 'b',
                         },
                     },
                 },
             },
             'output': {
                 'stdout': 'foo\nar\naz\n',
             },
         },
         {
             'name': 'Test: replace string in stdin, with count',
             'input': {
                 'cmdline': 'cat',
                 'stdin': {
                     'value': 'foo\nbar\nbaz\n',
                     'transform': {
                         'replace': {
                             'str': 'b',
                             'with': 'x',
                             'count': 1,
                         },
                     },
                 },
             },
             'output': {
                 'stdout': 'foo\nxar\nbaz\n',
             },
         },
         {
             'name': 'Test: replace regex in stdin',
             'input': {
                 'cmdline': 'cat',
                 'stdin': {
                     'value': 'foo\nbar\nbaz\n',
                     'transform': {
                         'replace': {
                             'regex': '[ao]',
                             'with': 'V',
                         },
                     },
                 },
             },
             'output': {
                 'stdout': 'fVV\nbVr\nbVz\n',
             },
         },
         {
             'name': 'Test: replace regex in stdin, refer to groups',
             'input': {
                 'cmdline': 'cat',
                 'stdin': {
                     'value': 'foo\nbar\nbaz\n',
                     'transform': {
                         'replace': {
                             'regex': '(.)([ao]+)',
                             'with': '\\2\\1',
                         },
                     },
                 },
             },
             'output': {
                 'stdout': 'oof\nabr\nabz\n',
             },
         },
         {
             'name': 'Test: replace regex in stdin, refer to named groups',
             'input': {
                 'cmdline': 'cat',
                 'stdin': {
                     'value': 'foo\nbar\nbaz\n',
                     'transform': {
                         'replace': {
                             'regex': '(?P<c>.)(?P<v>[ao]+)',
                             'with': '\\g<v>\\g<c>',
                         },
                     },
                 },
             },
             'output': {
                 'stdout': 'oof\nabr\nabz\n',
             },
         },
         {
             'name': 'Test: replace regex in stdin, /.../.../',
             'input': {
                 'cmdline': 'cat',
                 'stdin': {
                     'value': 'foo\nbar\nbaz\n',
                     'transform': {
                         'replace': '/[ao]/V/',
                     },
                 },
             },
             'output': {
                 'stdout': 'fVV\nbVr\nbVz\n',
             },
         },
         {
             'name': 'Test: replace regex in stdin, /.../.../, alt delim',
             'input': {
                 'cmdline': 'cat',
                 'stdin': {
                     'value': 'foo\nbar\nbaz\n',
                     'transform': {
                         'replace': '![ao]!V!',
                     },
                 },
             },
             'output': {
                 'stdout': 'fVV\nbVr\nbVz\n',
             },
         },
         {
             'name': 'Test: replace regex in stdin, /.../.../, refer to groups',
             'input': {
                 'cmdline': 'cat',
                 'stdin': {
                     'value': 'foo\nbar\nbaz\n',
                     'transform': {
                         'replace': '/(?P<c>.)(?P<v>[ao]+)/\\g<v>\\g<c>/',
                     },
                 },
             },
             'output': {
                 'stdout': 'oof\nabr\nabz\n',
             },
         },
         {
             'name': 'Test: replace regex in stdin, without "with"',
             'input': {
                 'cmdline': 'cat',
                 'stdin': {
                     'value': 'foo\nbar\nbaz\n',
                     'transform': {
                         'replace': {
                             'regex': '[ao]',
                         },
                     },
                 },
             },
             'output': {
                 'stdout': 'f\nbr\nbz\n',
             },
         },
         {
             'name': 'Test: replace regex in stdin, with "count"',
             'input': {
                 'cmdline': 'cat',
                 'stdin': {
                     'value': 'foo\nbar\nbaz\n',
                     'transform': {
                         'replace': {
                             'regex': '[ao]',
                             'with': 'V',
                             'count': 2,
                         },
                     },
                 },
             },
             'output': {
                 'stdout': 'fVV\nbar\nbaz\n',
             },
         },
         {
             'name': 'Test: replace regex in stdin',
             'input': {
                 'cmdline': 'cat',
                 'stdin': {
                     'value': 'foo\nbar\nbaz\n',
                     'transform': {
                         'replace': {
                             'regex': '[ao]',
                             'with': 'V',
                         },
                     },
                 },
             },
             'output': {
                 'stdout': 'fVV\nbVr\nbVz\n',
             },
         },
         {
             'name': 'Test: replace regex in stdin, with "reflags" (with "re.")',
             'input': {
                 'cmdline': 'cat',
                 'stdin': {
                     'value': 'foo\nbar\nbaz\n',
                     'transform': {
                         'replace': {
                             'regex': '[or] . b',
                             'with': '-',
                             'reflags': 're.DOTALL|re.VERBOSE',
                         },
                     },
                 },
             },
             'output': {
                 'stdout': 'fo-a-az\n',
             },
         },
         {
             'name': 'Test: replace regex in stdin, with "reflags" (without "re.")',
             'input': {
                 'cmdline': 'cat',
                 'stdin': {
                     'value': 'foo\nbar\nbaz\n',
                     'transform': {
                         'replace': {
                             'regex': '[or] . b',
                             'with': '-',
                             'reflags': 'DOTALL|VERBOSE',
                         },
                     },
                 },
             },
             'output': {
                 'stdout': 'fo-a-az\n',
             },
         },
         {
             'name': 'Test: replace regex in stdin, flags appended to "regex" (with "re.")',
             'input': {
                 'cmdline': 'cat',
                 'stdin': {
                     'value': 'foo\nbar\nbaz\n',
                     'transform': {
                         'replace': {
                             'regex re.DOTALL|re.VERBOSE': '[or] . b',
                             'with': '-',
                         },
                     },
                 },
             },
             'output': {
                 'stdout': 'fo-a-az\n',
             },
         },
         {
             'name': 'Test: replace regex in stdin, flags appended to "regex" (without "re.")',
             'input': {
                 'cmdline': 'cat',
                 'stdin': {
                     'value': 'foo\nbar\nbaz\n',
                     'transform': {
                         'replace': {
                             'regex DOTALL|VERBOSE': '[or] . b',
                             'with': '-',
                         },
                     },
                 },
             },
             'output': {
                 'stdout': 'fo-a-az\n',
             },
         },
         {
             'name': 'Test: list of replacements in stdin',
             'input': {
                 'cmdline': 'cat',
                 'stdin': {
                     'value': 'foo\nbar\nbaz\n',
                     'transform': {
                         'replace': [
                             {
                                 'regex': '[ao]',
                                 'with': 'V',
                             },
                             {
                                 'str': 'b',
                                 'with': 'x',
                             },
                             '/[xz]/a/',
                         ],
                     },
                 },
             },
             'output': {
                 'stdout': 'fVV\naVr\naVa\n',
             },
         },
         {
             'name': 'Test: transformations of None',
             'input': {
                 'cmdline': 'cat f1.txt f2.txt f3.txt f4.txt f5.txt f6.txt f7.txt',
                 'file:f1.txt': {
                     'value': None,
                     'transform': {
                         'prepend': 'foo\n'
                     },
                 },
                 'file:f2.txt': {
                     'value': None,
                     'transform': {
                         'append': 'foo\n'
                     },
                 },
                 'file:f3.txt': {
                     'value': None,
                     'transform': {
                         'filter-out': 'o'
                     },
                 },
                 'file:f4.txt': {
                     'value': None,
                     'transform': {
                         'replace': '/o/x/'
                     },
                 },
                 'file:f5.txt': {
                     'value': None,
                     'transform': {
                         'set-value': 'zz\n'
                     },
                 },
                 'file:f6.txt': {
                     'value': None,
                     'transform': {
                         'python': 'return "x\\n" if value is None else "y\\n"'
                     },
                 },
                 'file:f7.txt': {
                     'value': None,
                     'transform': {
                         'shell': 'tr "a" "b"'
                     },
                 },
             },
             'output': {
                 'stdout': 'foo\nfoo\nzz\nx\n',
                 'stderr': ('cat: f3.txt: No such file or directory\n'
                            'cat: f4.txt: No such file or directory\n'
                            'cat: f7.txt: No such file or directory\n'),
             },
         },
         {
             'name': 'Test: transformations of int: set-value',
             'input': {
                 'cmdline': 'cat foo',
             },
             'output': {
                 'stdout': '',
                 'stderr': 'cat: foo: No such file or directory\n',
                 'returncode': {
                     'value': 0,
                     'transform-expected': [
                         {'set-value': 1},
                     ],
                 },
             },
         },
         {
             'name': 'Test: transformations of int: implicit set-value',
             'input': {
                 'cmdline': 'cat foo',
             },
             'output': {
                 'stdout': '',
                 'stderr': 'cat: foo: No such file or directory\n',
                 'returncode': {
                     'value': 0,
                     'transform-expected': 1,
                 },
             },
         },
         {
             'name': 'Test: transformations of int: keep intact',
             'input': {
                 'cmdline': 'cat foo',
             },
             'output': {
                 'stdout': '',
                 'stderr': 'cat: foo: No such file or directory\n',
                 'returncode': {
                     'value': 1,
                     'transform-expected': [
                         {'prepend': 2},
                         {'append': 3},
                         {'filter-out': '3'},
                         {'replace': '/3/4/'},
                         {'set-value': 'foo'},
                         {'set-value': None},
                         # Implicit set-value
                         'bar',
                         None,
                     ],
                 },
             },
         },
         {
             'name': 'Test: transformations of int: Python',
             'input': {
                 'cmdline': 'cat foo',
             },
             'output': {
                 'stdout': '',
                 'stderr': 'cat: foo: No such file or directory\n',
                 'returncode': {
                     'value': 0,
                     'transform-expected': [
                         {'python': 'return value + 1'},
                     ],
                 },
             },
         },
         {
             'name': 'Test: transformations of int: shell',
             'input': {
                 'cmdline': 'cat foo',
             },
             'output': {
                 'stdout': '',
                 'stderr': 'cat: foo: No such file or directory\n',
                 'returncode': {
                     'value': 0,
                     'transform-expected': [
                         {'shell': 'tr 0 1'},
                     ],
                 },
             },
         },
         {
             'name': 'Test: transformation set-value str and None',
             'input': {
                 'cmdline': 'cat f1.txt f2.txt f3.txt f4.txt',
                 'file:f1.txt': {
                     'value': 'foo\n',
                     'transform': {
                         # Should not change
                         'set-value': 1,
                     },
                 },
                 'file:f2.txt': {
                     'value': 'bar\n',
                     'transform': {
                         # Should change
                         'set-value': None,
                     },
                 },
                 'file:f3.txt': {
                     'value': None,
                     'transform': {
                         # Should not change
                         'set-value': 1,
                     },
                 },
                 'file:f4.txt': {
                     'value': None,
                     'transform': {
                         # Should change
                         'set-value': 'baz\n',
                     },
                 },
             },
             'output': {
                 'stdout': 'foo\nbaz\n',
                 'stderr': ('cat: f2.txt: No such file or directory\n'
                            'cat: f3.txt: No such file or directory\n'),
                 'returncode': 1,
             },
         },
         {
             'name': 'Test: transformations of expected list (test "in")',
             'input': {
                 'cmdline': 'cat',
                 'stdin': 'foo\nbar\n',
             },
             'output': {
                 'stdout': [
                     {
                         'test': 'in',
                         'value': [
                             'foo\nbar\n',
                             'xxx\n',
                         ],
                     },
                 ],
             },
             'transform': [
                 {},
                 {
                     'input': {
                         'stdin': {
                             'prepend': 'foo\n',
                         },
                     },
                     'output-expected': {
                         'stdout': {
                             'prepend': 'foo\n',
                         },
                     },
                 },
                 {
                     'input': {
                         'stdin': {
                             'append': 'foo\n',
                         },
                     },
                     'output-expected': {
                         'stdout': {
                             'append': 'foo\n',
                         },
                     },
                 },
                 {
                     'input': {
                         'stdin': {
                             'filter-out': 'foo\n',
                         },
                     },
                     'output-expected': {
                         'stdout': {
                             'filter-out': 'foo\n',
                         },
                     },
                 },
                 {
                     'input': {
                         'stdin': {
                             'replace': '/f/b/',
                         },
                     },
                     'output-expected': {
                         'stdout': {
                             'replace': '/f/b/',
                         },
                     },
                 },
                 {
                     'input': {
                         'stdin': {
                             'set-value': 'zzz\n',
                         },
                     },
                     'output-expected': {
                         'stdout': {
                             'set-value': 'zzz\n',
                         },
                     },
                 },
                 {
                     'input': {
                         'stdin': {
                             'python': 'return value[2:]',
                         },
                     },
                     'output-expected': {
                         'stdout': {
                             'python': 'return value[2:]',
                         },
                     },
                 },
                 {
                     'input': {
                         'stdin': {
                             'shell': 'tr z x',
                         },
                     },
                     'output-expected': {
                         'stdout': {
                             'shell': 'tr z x',
                         },
                     },
                 },
             ],
         },
         {
             # "not-in" is tested separately from "in", as
             # transformation "set-value" would not produce
             # correct-results for "not-in"
             'name': 'Test: transformations of expected list (test "not-in")',
             'input': {
                 'cmdline': 'cat',
                 'stdin': 'foo\nbar\n',
             },
             'output': {
                 'stdout': [
                     {
                         'test': 'not-in',
                         'value': [
                             'foo\nbar\nbaz\n',
                             'xxx\n',
                         ],
                     },
                 ],
             },
             'transform': [
                 {},
                 {
                     'input': {
                         'stdin': {
                             'prepend': 'foo\n',
                         },
                     },
                     'output-expected': {
                         'stdout': {
                             'prepend': 'foo\n',
                         },
                     },
                 },
                 {
                     'input': {
                         'stdin': {
                             'append': 'foo\n',
                         },
                     },
                     'output-expected': {
                         'stdout': {
                             'append': 'foo\n',
                         },
                     },
                 },
                 {
                     'input': {
                         'stdin': {
                             'filter-out': 'foo\n',
                         },
                     },
                     'output-expected': {
                         'stdout': {
                             'filter-out': 'foo\n',
                         },
                     },
                 },
                 {
                     'input': {
                         'stdin': {
                             'replace': '/f/b/',
                         },
                     },
                     'output-expected': {
                         'stdout': {
                             'replace': '/f/b/',
                         },
                     },
                 },
                 {
                     'input': {
                         'stdin': {
                             'python': 'return value[2:]',
                         },
                     },
                     'output-expected': {
                         'stdout': {
                             'python': 'return value[2:]',
                         },
                     },
                 },
                 {
                     'input': {
                         'stdin': {
                             'shell': 'tr z x',
                         },
                     },
                     'output-expected': {
                         'stdout': {
                             'shell': 'tr z x',
                         },
                     },
                 },
             ],
         },
         {
             'name': 'Test: transformation sequences',
             'input': {
                 'cmdline': 'cat',
                 'stdin': {
                     'value': 'foo\nbar\nbaz\n',
                     'transform': [
                         {'prepend': 'foo1\n'},
                         {'prepend': 'foo0\n'},
                         {'filter-out': 'o'},
                     ],
                 },
             },
             'output': {
                 'stdout': {
                     'value': 'foo\n',
                     'transform-expected': [
                         {'append': 'bar\n'},
                         {'append': 'baz\n'},
                         {'prepend': 'foo1\n'},
                         {'prepend': 'foo0\n'},
                         {'filter-out': 'o'},
                     ],
                 },
                 'stderr': '',
                 'returncode': 0,
             },
         },
         {
             'name': 'Test: global, file-specific and test-specific transformations',
             'input': {
                 'cmdline': 'tee file.out',
                 'stdin': {
                     'value': 'foo\nbar\nbaz\nzoo\n',
                 },
             },
             'output': {
                 'transform-expected': [
                     {'append': 'zoo\n'},
                 ],
                 'transform-actual': [
                     {'filter-out': 'b'},
                 ],
                 # Actual is now 'foo\nar\naz\nzoo\n'
                 'stdout': [
                     {
                         'regex DOTALL': 'foo\n.*',
                         # Does not match, as "zoo\n" is appended to the
                         # expected value
                         'not-regex': ['foo\n', 'zooz'],
                     },
                     {
                         'transform-expected': [
                             { 'filter-out': 'z' },
                         ],
                         'transform-actual': [
                             { 'append': 'goo\n' },
                         ],
                     },
                     # Actual is now 'foo\nar\naz\nzoo\ngoo\n'
                     {
                         # z's are filtered out from the expected value, so
                         # "zz" should match
                         'regex': ['zz', 'g'],
                     },
                     {
                         'transform-expected': [
                             { 'filter-out': 'b' },
                             { 'append': 'goo\n' },
                         ],
                         'transform-actual': [
                             # No-op for "bar\n" as "b" has been filtered out
                             { 'filter-out': ['bar\n', 'z'] },
                         ],
                         'value': 'foo\nbar\nbaz\n',
                     },
                 ],
                 'file:file.out': {
                     # Global transformations apply ("zoo\n" appended to
                     # expected values)
                     'regex': 'az\n',
                     # But transformations specific to stdout do not
                     'not-regex': ['az', 'zoo', 'goo'],
                 },
                 # Global transformations apply
                 'stderr': {
                     'value': '',
                     'transform-actual': [
                         { 'append': 'zoo\n' },
                     ],
                 },
                 'returncode': 0,
             },
         },
         {
             'name': 'Test: global, file-specific and test-specific transformations, with transform instead of transform-expected',
             'input': {
                 'cmdline': 'tee file.out',
                 'stdin': {
                     'value': 'foo\nbar\nbaz\nzoo\n',
                 },
             },
             'output': {
                 'transform': [
                     {'append': 'zoo\n'},
                 ],
                 'transform-actual': [
                     {'filter-out': 'b'},
                 ],
                 # Actual is now 'foo\nar\naz\nzoo\n'
                 'stdout': [
                     {
                         'regex DOTALL': 'foo\n.*',
                         # Does not match, as "zoo\n" is appended to the
                         # expected value
                         'not-regex': ['foo\n', 'zooz'],
                     },
                     {
                         'transform': [
                             { 'filter-out': 'z' },
                         ],
                         'transform-actual': [
                             { 'append': 'goo\n' },
                         ],
                     },
                     # Actual is now 'foo\nar\naz\nzoo\ngoo\n'
                     {
                         # z's are filtered out from the expected value, so
                         # "zz" should match
                         'regex': ['zz', 'g'],
                     },
                     {
                         'transform': [
                             { 'filter-out': 'b' },
                             { 'append': 'goo\n' },
                         ],
                         'transform-actual': [
                             # No-op for "bar\n" as "b" has been filtered out
                             { 'filter-out': ['bar\n', 'z'] },
                         ],
                         'value': 'foo\nbar\nbaz\n',
                     },
                 ],
                 'file:file.out': {
                     # Global transformations apply ("zoo\n" appended to
                     # expected values)
                     'regex': 'az\n',
                     # But transformations specific to stdout do not
                     'not-regex': ['az', 'zoo', 'goo'],
                 },
                 # Global transformations apply
                 'stderr': {
                     'value': '',
                     'transform-actual': [
                         { 'append': 'zoo\n' },
                     ],
                 },
                 'returncode': 0,
             },
         },
         {
             'name': 'Test: global transformation groups',
             'input': {
                 'cmdline': 'cat',
                 'shell': True,
                 'stdin': 'foo\nbar\nbaz\n',
             },
             'output': {
                 'stdout': {
                     'value': 'foo\nbar\nbaz\n',
                 },
             },
             'transform': [
                 {},  # No transformations
                 {
                     'input': {
                         'stdin': {
                             'append': 'zoo\n',
                         },
                     },
                     'output-expected': {
                         'stdout': {
                             'append': 'zoo\n',
                         },
                     },
                 },
                 {
                     'input': {
                         'stdin': [
                             {'append': 'zoo\n'},
                             {'replace': '/o/a/'},
                         ],
                     },
                     'output-expected': {
                         'stdout': [
                             {'append': 'zoo\n'},
                             {'replace': '/o/a/'},
                         ],
                     },
                 },
                 {
                     'input': {
                         'stdin': {
                             'append': 'xxx\n',
                         },
                     },
                     'output-actual': {
                         'stdout': {
                             'filter-out': 'xxx\n',
                         },
                     },
                 },
             ],
         },
         {
             'name': 'Test: global transformation groups, output instead of output-expected',
             'input': {
                 'cmdline': 'cat',
                 'shell': True,
                 'stdin': 'foo\nbar\nbaz\n',
             },
             'output': {
                 'stdout': {
                     'value': 'foo\nbar\nbaz\n',
                 },
             },
             'transform': [
                 {
                     'input': {
                         'stdin': {
                             'append': 'zoo\n',
                         },
                     },
                     'output': {
                         'stdout': {
                             'append': 'zoo\n',
                         },
                     },
                 },
                 {
                     'input': {
                         'stdin': [
                             {'append': 'zoo\n'},
                             {'replace': '/o/a/'},
                         ],
                     },
                     'output': {
                         'stdout': [
                             {'append': 'zoo\n'},
                             {'replace': '/o/a/'},
                         ],
                     },
                 },
             ],
         },
         {
             'name': 'Test: global transformation group, mixing files, file:F',
             'input': {
                 'cmdline': 'cat input.txt > output.txt',
                 'shell': True,
                 'file:input.txt': 'foo\nbar\nbaz\n',
             },
             'output': {
                 'files': {
                     'output.txt': 'foo\nbar\nbaz\n',
                 },
             },
             'transform': [
                 {
                     'input': {
                         'files': {
                             'input.txt': {
                                 'append': 'zoo\n',
                             },
                         },
                     },
                     'output-expected': {
                         'file:output.txt': {
                             'append': 'zoo\n',
                         },
                     },
                 },
             ],
         },
         {
             'name': 'Test: global transformation group, transform cmdline',
             'input': {
                 'cmdline': 'cat input.txt',
                 'shell': True,
                 'file:input.txt': 'foo\nbar\nbaz\n',
             },
             'output': {
                 'stdout': 'foo\nbar\nbaz\n',
                 'stderr': '',
                 'returncode': 0,
             },
             'transform': [
                 {
                     'input': {
                         'cmdline': {
                             'append': ' > output.txt'
                         },
                     },
                     'output-expected': {
                         'file:output.txt': {
                             'set-value': 'foo\nbar\nbaz\n',
                         },
                         'stdout': {
                             'set-value': '',
                         },
                     },
                 },
                 {
                     'input': {
                         'cmdline': {
                             'append': ' input2.txt'
                         },
                         'file:input2.txt': {
                             'set-value': 'zoo\n',
                         },
                     },
                     'output-expected': {
                         'stdout': {
                             'append': 'zoo\n',
                         },
                     },
                 },
                 {
                     'input': {
                         'cmdline': {
                             'append': ' input2.txt',
                         },
                     },
                     'output-expected': {
                         'stderr': {
                             'set-value': 'cat: input2.txt: No such file or directory\n',
                         },
                         'returncode': {
                             'set-value': 1,
                         }
                     },
                 },
                 # Implicit set-value
                 {
                     'input': {
                         'cmdline': 'cat input.txt input2.txt',
                     },
                     'output-expected': {
                         'stderr': 'cat: input2.txt: No such file or directory\n',
                         'returncode': 1,
                     },
                 },
             ],
         },
         {
             'name': 'Test: transformation groups and global transformations',
             'input': {
                 'cmdline': 'cat',
                 'stdin': 'foo\nbar\nbaz\n',
             },
             'output': {
                 # Global transformations
                 'transform-expected': [
                     {'filter-out': 'z'},
                 ],
                 'transform-actual': [
                     {'filter-out': 'z'},
                 ],
                 'stdout': 'foo\nbar\nbaz\n',
                 # After transformation: 'foo\nbar\nba\n'
             },
             'transform': [
                 {},  # No transformations
                 {
                     'input': {
                         'stdin': {
                             'append': 'zoo\n',
                         },
                     },
                     'output-expected': {
                         'stdout': {
                             # Global transformations applied before this
                             'append': 'oo\n',
                         },
                     },
                 },
             ],
         },
         {
             'name': 'Test: transformation groups and global transformations (without "-expected")',
             'input': {
                 'cmdline': 'cat',
                 'stdin': 'foo\nbar\nbaz\n',
             },
             'output': {
                 # Global transformations
                 'transform': [
                     {'filter-out': 'z'},
                 ],
                 'transform-actual': [
                     {'filter-out': 'z'},
                 ],
                 'stdout': 'foo\nbar\nbaz\n',
                 # After transformation: 'foo\nbar\nba\n'
             },
             'transform': [
                 {},  # No transformations
                 {
                     'input': {
                         'stdin': {
                             'append': 'zoo\n',
                         },
                     },
                     'output': {
                         'stdout': {
                             # Global transformations applied before this
                             'append': 'oo\n',
                         },
                     },
                 },
             ],
         },
         {
             'name': 'Test: transformation groups and file-specific transformations',
             'input': {
                 'cmdline': 'cat',
                 'stdin': 'foo\nbar\nbaz\n',
             },
             'output': {
                 # File-specific transformations
                 'stdout': {
                     # After transformation: 'foo\nbar\nba\n'
                     'value': 'foo\nbar\nbaz\n',
                     'transform-expected': [
                         {'filter-out': 'z'},
                     ],
                     'transform-actual': [
                         {'filter-out': 'z'},
                     ],
                 },
             },
             'transform': [
                 {},  # No transformations
                 {
                     'input': {
                         'stdin': {
                             'append': 'zoo\n',
                         },
                     },
                     'output-expected': {
                         'stdout': {
                             # File-specific transformations applied before this
                             'append': 'oo\n',
                         },
                     },
                 },
             ],
         },
         {
             'name': 'Test: transformation groups and file-specific transformations (without -expected)',
             'input': {
                 'cmdline': 'cat',
                 'stdin': 'foo\nbar\nbaz\n',
             },
             'output': {
                 # File-specific transformations
                 'stdout': {
                     # After transformation: 'foo\nbar\nba\n'
                     'value': 'foo\nbar\nbaz\n',
                     'transform': [
                         {'filter-out': 'z'},
                     ],
                     'transform-actual': [
                         {'filter-out': 'z'},
                     ],
                 },
             },
             'transform': [
                 {},  # No transformations
                 {
                     'input': {
                         'stdin': {
                             'append': 'zoo\n',
                         },
                     },
                     'output': {
                         'stdout': {
                             # File-specific transformations applied before this
                             'append': 'oo\n',
                         },
                     },
                 },
             ],
         },
         {
             'name': 'Test: transformation groups and test-specific transformations',
             'input': {
                 'cmdline': 'cat',
                 'stdin': 'foo\nbar\nbaz\n',
             },
             'output': {
                 'stdout': [
                     {'value': 'foo\nbar\nbaz\n'},
                     # Test-specific transformations
                     {
                         'transform-expected': [
                             {'filter-out': 'x'},
                         ],
                         'transform-actual': [
                             {'filter-out': 'z'},
                         ],
                     },
                     # After transformation: 'foo\nbar\nba\n'
                     {'value': 'foox\nbarx\nba\n'},
                 ],
             },
             'transform': [
                 {},  # No transformations
                 {
                     # These should work for the above value tests
                     # both before and after the test-specific
                     # transformations
                     'input': {
                         'stdin': {
                             'append': 'yyy\n',
                         },
                     },
                     'output-expected': {
                         'stdout': {
                             'append': 'yyy\n',
                         },
                     },
                 },
             ],
         },
         {
             'name': 'Test: transformation groups and test-specific transformations (without -expected)',
             'input': {
                 'cmdline': 'cat',
                 'stdin': 'foo\nbar\nbaz\n',
             },
             'output': {
                 'stdout': [
                     {'value': 'foo\nbar\nbaz\n'},
                     # Test-specific transformations
                     {
                         'transform': [
                             {'filter-out': 'x'},
                         ],
                         'transform-actual': [
                             {'filter-out': 'z'},
                         ],
                     },
                     # After transformation: 'foo\nbar\nba\n'
                     {'value': 'foox\nbarx\nba\n'},
                 ],
             },
             'transform': [
                 {},  # No transformations
                 {
                     # These should work for the above value tests
                     # both before and after the test-specific
                     # transformations
                     'input': {
                         'stdin': {
                             'append': 'yyy\n',
                         },
                     },
                     'output': {
                         'stdout': {
                             'append': 'yyy\n',
                         },
                     },
                 },
             ],
         },
         {
             'name': 'Test: transformation groups and dict with test names',
             'input': {
                 'cmdline': 'cat',
                 'stdin': 'foo\nbar\nbaz\n',
             },
             'output': {
                 'stdout': {
                     '==': 'foo\nbar\nbaz\n',
                     '!=': 'goo',
                     'contains': [
                         'foo\n',
                         'baz\n',
                     ],
                     'regex': 'b..\n',
                 },
             },
             'transform': [
                 {},  # No transformations
                 {
                     'input': {
                         'stdin': {
                             'replace': '/\n/yyy\n/',
                         },
                     },
                     'output-expected': {
                         'stdout': {
                             'replace': '/\n/yyy\n/',
                         },
                     },
                 },
                 {
                     'input': {
                         'stdin': {
                             'append': 'xxx\n',
                         },
                     },
                     'output-actual': {
                         'stdout': {
                             'filter-out': 'xxx\n',
                         },
                     },
                 },
             ],
         },
         {
             'name': 'Test: transformation group names',
             'input': {
                 'cmdline': 'cat',
                 'stdin': 'foo\nbar\nbaz\n',
             },
             'output': {
                 'stdout': 'foo\nbar\nbaz\n',
             },
             'transform': [
                 {},  # No transformations
                 {
                     'name': 'trans 1',
                     'input': {
                         'stdin': {
                             'replace': '/\n/yyy\n/',
                         },
                     },
                     'output-expected': {
                         'stdout': {
                             'replace': '/\n/yyy\n/',
                         },
                     },
                 },
                 {
                     'name': 'trans 2',
                     'input': {
                         'stdin': {
                             'append': 'xxx\n',
                         },
                     },
                     'output-actual': {
                         'stdout': {
                             'filter-out': 'xxx\n',
                         },
                     },
                 },
             ],
         },
         {
             'name': 'Test: "files" in input and output',
             'input': {
                 'cmdline': 'cat a.txt b.txt | tee out1.txt > out2.txt',
                 'shell': True,
                 'files': {
                     'a.txt': 'a\n',
                     'b.txt': {
                         'value': 'b\n',
                     },
                 },
                 'stdin': '',
             },
             'output': {
                 'files': {
                     'out1.txt': 'a\nb\n',
                     'out2.txt': {
                         'value': 'a\nb\n',
                     },
                 },
                 'stdout': '',
                 'stderr': '',
                 'returncode': 0,
             },
         },
         # Multiple inputs with the same output
         {
             'name': 'Test: multiple inputs with same output',
             'input': [
                 {
                     'name': 'cat file',
                     'cmdline': 'cat infile.txt',
                     'file:infile.txt': 'test1\ntest2\n'
                 },
                 {
                     'name': 'cat redirect file',
                     'cmdline': 'cat < infile.txt',
                     'shell': True,
                     'file:infile.txt': 'test1\ntest2\n'
                 },
                 {
                     'name': 'cat stdin',
                     'cmdline': 'cat',
                     'stdin': 'test1\ntest2\n'
                 },
                 {
                     # Without 'name'
                     'prog': 'cat',
                     'stdin': 'test1\ntest2\n'
                 },
                 {
                     'name': 'printf',
                     'cmdline': 'printf "test1\\ntest2\\n"',
                     'shell': True,
                 },
             ],
             'output': {
                 'stdout': 'test1\ntest2\n',
                 'stderr': '',
                 'returncode': 0,
             },
         },
         {
             'name': 'Test: multiple cmdlines in input',
             'input': {
                 'cmdline': [
                     'cat infile.txt',
                     'cat < infile.txt',
                     'printf "test1\\ntest2\\n"',
                 ],
                 'shell': True,
                 'file:infile.txt': 'test1\ntest2\n'
             },
             'output': {
                 'stdout': 'test1\ntest2\n',
                 'stderr': '',
                 'returncode': 0,
             },
         },
         {
             'name': 'Test: multiple cmdlines and alternative input files',
             'input': {
                 'cmdline': [
                     'grep -h "test" infile1.txt infile2.txt',
                     'grep -hv "[abc]" infile1.txt infile2.txt',
                     'cat infile1.txt infile2.txt | grep "test"',
                 ],
                 'shell': True,
                 'file:infile1.txt': [
                     'aaaa\ntest1\n',
                     'bbbb\ntest1\n',
                     'cccc\ntest1\n',
                 ],
                 'file:infile2.txt': [
                     'aaaa\ntest2\n',
                     'bbbb\ntest2\n',
                     'cccc\ntest2\n',
                 ],
             },
             'output': {
                 'stdout': 'test1\ntest2\n',
                 'stderr': '',
                 'returncode': 0,
             },
         },
         {
             'name': 'Test: multiple cmdlines and alt input files as "files"',
             'input': {
                 'cmdline': [
                     'grep -h "test" infile1.txt infile2.txt',
                     'grep -hv "[abc]" infile1.txt infile2.txt',
                 ],
                 'shell': True,
                 'files': [
                     {
                         'infile1.txt': 'aaaa\ntest1\n',
                         'infile2.txt': 'aaaa\ntest2\n',
                     },
                     {
                         'infile1.txt': '',
                         'infile2.txt': 'aaaa\ntest1\ntest2\n',
                     },
                 ],
             },
             'output': {
                 'stdout': 'test1\ntest2\n',
                 'stderr': '',
                 'returncode': 0,
             },
         },
         {
             'name': 'Test: multiple cmdlines and envvars',
             'input': {
                 'cmdline': [
                     'echo "$FOO$SEP$BAR"',
                     'echo "$FOO-$BAR"',
                 ],
                 'shell': True,
                 'envvars': [
                     {
                         'FOO': 'x',
                         'SEP': '-',
                         'BAR': 'y',
                     },
                     {
                         'FOO0': 'x',
                         'FOO': '$FOO0',
                         'SEP': '-',
                         'BAR': 'y',
                     },
                 ],
             },
             'output': {
                 'stdout': 'x-y\n',
                 'stderr': '',
                 'returncode': 0,
             },
         },
         {
             'name': 'Test: multiple named inputs with multiple alternatives',
             'input': [
                 {
                     'name': 'grep',
                     'cmdline': [
                         'grep -h "test" infile1.txt infile2.txt',
                         'grep -hv "[abc]" infile1.txt infile2.txt',
                     ],
                     'shell': True,
                     'file:infile1.txt': [
                         'aaaa\ntest1\n',
                         'bbbb\ntest1\n',
                     ],
                     'file:infile2.txt': [
                         'aaaa\ntest2\n',
                         'bbbb\ntest2\n',
                     ],
                 },
                 {
                     'name': 'cat',
                     'cmdline': [
                         'cat infile1.txt infile2.txt',
                         'cat infile3.txt',
                     ],
                     'file:infile1.txt': 'test1\n',
                     'file:infile2.txt': 'test2\n',
                     'file:infile3.txt': 'test1\ntest2\n',
                 },
                 {
                     'name': 'printf',
                     'cmdline': [
                         'printf "test1\\ntest2\\n"',
                         'printf "test1\ntest2\n"',
                     ],
                     'shell': True,
                 },
             ],
             'output': {
                 'stdout': 'test1\ntest2\n',
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
                 'stdout': '',
             },
         },
         {
             'name': 'Test: skipping test with reason',
             'status': 'skip: Test skipping',
             'input': {
             },
             'output': {
                 'stdout': '',
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
                 'stdout': '',
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
                 'stdout': 'test1\ntest2\n',
             },
         },
         {
             'name': 'Test: xfailing test',
             'status': 'xfail',
             'input': {
                 'cmdline': 'echo test'
             },
             'output': {
                 'stdout': '',
             },
         },
         {
             'name': 'Test: xfailing test with reason',
             'status': 'xfail: Test xfailing',
             'input': {
                 'cmdline': 'echo test'
             },
             'output': {
                 'stdout': '',
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

    def count_tests(testcase_conts):
        # FIXME: This does not yet count correctly. Maybe we should add tests
        # for this function?
        count = 0
        default_values = {}
        for tc in testcase_conts:
            # print(tc)
            if 'defaults' in tc:
                default_values = dict_deep_update(
                    default_values, deepcopy(tc['defaults']))
                # print('defaults ->', default_values)
            else:
                output = dict_deep_update(
                    deepcopy(default_values.get('output')),
                    tc.get('output', {}))
                # print('output', output)
                # print('count', count, '-> ', end='')
                for outputitem in output:
                    if (outputitem in ['stdout', 'stderr', 'returncode']
                            or outputitem.startswith('file:')):
                        tests = output[outputitem]
                        if not isinstance(tests, list):
                            tests = [tests]
                        for test in tests:
                            if (isinstance(test, dict)
                                    and 'value' not in test):
                                for val in test.values():
                                    if isinstance(val, list):
                                        count += len(val)
                                    elif val not in ['transform',
                                                     'transform-expected',
                                                     'transform-actual']:
                                        count += 1
                            else:
                                count += 1
                # print(count)
        return count

    def getitem(value):
        if isinstance(value, list) or isinstance(value, tuple):
            return value[0]
        else:
            return value

    fname_testcase_contents, testcase_filespecs = testcase_files
    testcases = collect_testcases(*testcase_filespecs, basedir=str(tmpdir))
    # print(testcases)
    # FIXME: Uncomment the following when count_tests works correctly.
    # assert len(testcases) == sum(
    #     count_tests(tc_conts) for _, tc_conts in fname_testcase_contents)
    testcase_num = 0
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
            assert len(testcase) == 4
            name, input_, inputitem, expected = (
                getitem(item) for item in testcase)
            # TODO: Test the values more thoroughly
            assert isinstance(name, str)
            assert isinstance(input_, dict)
            assert (inputitem in ['stdout', 'stderr', 'returncode']
                    or inputitem.startswith('file:'))
            assert isinstance(expected, dict)
            exp_val = expected.get('value')
            assert ((isinstance(exp_val, str) and inputitem != 'returncode')
                    or (isinstance(exp_val, int)
                        and inputitem == 'returncode')
                    or (isinstance(exp_val, list)
                        and expected['test'] in ['in', 'not-in'])
                    or (isinstance(exp_val, dict) and len(exp_val) == 1
                        and list(exp_val.keys())[0] in ['file', 'python',
                                                        'shell'])
                    or (exp_val is None and inputitem.startswith('file:')))
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
    check({}, None, {})
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
                           'input': {'cmdline': ''}},
                          '', None,
                          tmpdir=str(tmpdir))
    with pytest.raises(ValueError) as e_info:
        check_program_run('Empty input info',
                          {'name': 'Empty input info',
                           'input': {}},
                          '', None,
                          tmpdir=str(tmpdir))
    with pytest.raises(ValueError) as e_info:
        check_program_run('Empty prog',
                          {'name': 'Empty prog',
                           'input': {'prog': ''}},
                          '', None,
                          tmpdir=str(tmpdir))
    with pytest.raises(ValueError) as e_info:
        check_program_run('Empty input args',
                          {'name': 'Empty input args',
                           'input': {'args': []}},
                          '', None,
                          tmpdir=str(tmpdir))


def test_unknown_keys(tmpdir):
    """Test with unknown keys in test cases."""
    # Unknown key at top level
    with pytest.raises(ValueError) as e_info:
        expand_testcases([('fname', [{'unknown': 'test'}])])
    # Unknown key in "input"
    with pytest.raises(ValueError) as e_info:
        expand_testcases([('fname', [{'input': {'cmdlinex': 'test'},
                                      'output': {'stdout': ''}}])])
    # Unknown key in "output"
    with pytest.raises(ValueError) as e_info:
        expand_testcases([('fname', [{'input': {'cmdline': 'test'},
                                      'output': {'transformx': 'test'}}])])
    # Unknown key in "transform"
    with pytest.raises(ValueError) as e_info:
        expand_testcases([('fname', [{'input': {'cmdline': 'test'},
                                      'output': {'stdout': ''},
                                      'transform': [{'outputx': 'test'}]}])])
    # Unknown key in "defaults"
    with pytest.raises(ValueError) as e_info:
        expand_testcases([('fname', [{'defaults': {'test': 'test'}}])])
    # "defs" should allow any keys
    expand_testcases([('fname', [{'defs': {'a': 'b', 'c': 'd'}}])])


def test_duplicate_filename(tmpdir):
    """Test with a file specified as both file:fname and files: {fname}."""
    with pytest.raises(ValueError) as e_info:
        check_program_run('Duplicate input file name',
                          {'name': 'Duplicate input file name',
                           'input': {
                               'cmdline': 'cat a',
                               'files': {'a': ''},
                               'file:a': '',
                           }},
                          '', None,
                          tmpdir=str(tmpdir))
        check_program_run('Duplicate output file name',
                          {'name': 'Duplicate output file name',
                           'input': {'cmdline': 'cat'},
                           'output': {
                               'files': {'a': ''},
                               'file:a': '',
                           }},
                          '', None,
                          tmpdir=str(tmpdir))


@pytest.mark.parametrize("name, input, outputitem, expected",
                         _testcases, ids=make_param_id)
def test_check_program_run(name, input, outputitem, expected, tmpdir):
    """Test scripttestlib.check_program_run with the testcases."""
    check_program_run(name, input, outputitem, expected, tmpdir=str(tmpdir))
