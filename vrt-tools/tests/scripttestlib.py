#! /usr/bin/env python3


"""
scripttestlib.py

A module for processing tests of complete scripts, for running with
pytest.

Please see README.md and the docstrings of functions for more
information.
"""


import glob
import importlib
import os
import os.path
import re
import shlex
import sys

from subprocess import Popen, PIPE

import pytest
import yaml


def _re_search(patt, val, flags=''):
    """Wrap re.search: Flags as a string (re. prefixes can be omitted)."""
    if flags:
        flags = eval('|'.join(
            ('re.' if not flag.startswith('re.') else '') + flag
            for flag in flags.split('|')))
    return re.search(patt, val, flags=(flags or 0))


_output_tests = {
    # Tests that can be used for testing output values: key is test name, value
    # is a two-argument boolean function, where the first argument is the
    # expected and the second the actual value.
    '==': lambda exp, val, *opts: val == exp,
    '!=': lambda exp, val, *opts: val != exp,
    '<': lambda exp, val, *opts: val < exp,
    '<=': lambda exp, val, *opts: val <= exp,
    '>': lambda exp, val, *opts: val > exp,
    '>=': lambda exp, val, *opts: val >= exp,
    'in': lambda exp, val, *opts: val in exp,
    'not_in': lambda exp, val, *opts: val not in exp,
    'matches': lambda exp, val, *opts: _re_search(exp, val, *opts) is not None,
    'not_matches': lambda exp, val, *opts: _re_search(exp, val, *opts) is None,
}


def collect_testcases(*filespecs, basedir=None):
    """Return a list of tuples (name, input, output) for the test cases
    found in the files matching one of filespecs in the directory
    `basedir`. The test cases are either in Python modules in a variable
    named `testcases` or in YAML files.
    """
    testcases = []
    if basedir is not None:
        sys.path[0:0] = [basedir]
    # Invalidate import caches just in case, as the Python modules might have
    # been constructed on-the-fly
    importlib.invalidate_caches()
    for filespec in filespecs:
        if basedir is not None:
            filespec = os.path.join(basedir, filespec)
        for fname in glob.iglob(filespec):
            if fname.endswith('.py'):
                # print(basedir, sys.path)
                testcases.extend(
                    importlib.import_module(os.path.basename(fname)[:-3])
                    .testcases)
            elif fname.endswith(('.yaml', '.yml')):
                with open(fname, 'r') as yf:
                    testcases.extend(item for items in yaml.safe_load_all(yf)
                                     for item in items)
    return expand_testcases(testcases)


def expand_testcases(testcases_dictlist):
    """Convert a list of test case dicts to a list of tuples."""
    testcases = []
    for tc in testcases_dictlist:
        params = (tc.get('name', {}), tc.get('input', {}),
                  tc.get('output') or tc.get('expected', {}))
        # If status start swith "xfail", "skip" or "skipif", mark the test
        # accordingly.
        if tc.get('status'):
            status, _, reason = tc['status'].partition(':')
            reason = reason.strip() or None
            if status == 'skipif':
                mark = pytest.mark.skipif(reason)
            elif status in ('skip', 'xfail'):
                mark = getattr(pytest.mark, status)(reason=reason)
            testcases.append(pytest.param(*params, marks=mark))
        else:
            testcases.append(params)
    return testcases


def add_output_test(name, test_fn):
    """Add output test `name` and its binary boolean function `test_fn`."""
    _output_tests[name] = test_fn


def check_program_run(name, input_, expected, tmpdir, progpath=None):
    """Check a program run: execute a single test case.

    Arguments:
      `name`: A name or description of the test (str)
      `input_`: A dict containing input information for the test:
          `prog`: program (script) name (str)
          `args`: command-line arguments, either a single string with
              arguments quoted as in shell, or as a list of unquoted strings
          `cmdline`: complete command line (str), with arguments quoted as
              in shell (an alternative to `prog` and `args`)
          `envvars`: a dict of environment variable values
          `stdin`: the content of standard input (str)
          `file:FNAME`: the content of file FNAME (str)
      `expected`: Expected output for the test (dict):
          `returncode`: program return code (int)
          `stdout`: the content of standard output (str)
          `stderr`: the content of standard error (str)
          `file:FNAME`: the content of file FNAME (str)
          The values may have several different forms:
          - simple scalar value, in which case the actual value is
            compared for equality with it;
          - a dict of two items: `test` is the test name (key in
            `_output_tests`) and `value` the expected value;
          - a dict with test names (keys in `_output_tests`) as keys
            and expected values as values (the value may also be a
            list in which case each item in the list is treated as a
            separate value to be tested); or
          - a list whose items may be any of the other: all tests must
            pass.
      `tmpdir`: The temporary directory in which to run the tests (the
          working directory for the commands and the base directory for
          input and output files)
      `progpath`: The directory or directories from which to search
          for the programs (scripts) to be run. Multiple directories are
          separated with colons and `{PATH}` is replaced with the current
          value of `$PATH`. If None, use the current `$PATH`.

    All input and output is currently assumed to be encoded in UTF-8.
    """
    # TODO: Possible enhancements:
    # - Allow specifying the search path for the program to be run.
    # - Allow specifying input and output encodings.
    shell = input_.get('shell', False)
    if 'cmdline' in input_:
        if shell:
            args = input_['cmdline']
        else:
            args = shlex.split(input_['cmdline'])
            prog = args[0]
    else:
        shell = False
        args = input_.get('args', [])
        args = shlex.split(args) if isinstance(args, str) else args
        prog = input_.get('prog')
        if prog:
            args[0:0] = [prog]
        else:
            prog = args[0]
    if 'envvars' in input_ or progpath is not None:
        env = dict(os.environ)
        if 'envvars' in input_:
            env.update(input_['envvars'])
        if progpath is not None:
            env['PATH'] = progpath.format(PATH=env.get('PATH'))
    else:
        env = None
    # print(env)
    stdin = input_.get('stdin', '').encode('UTF-8')
    for key, value in input_.items():
        if key.startswith('file:'):
            fname = key.split(':', maxsplit=1)[1]
            dirname = os.path.dirname(fname)
            if dirname:
                os.makedirs(os.path.join(tmpdir, dirname), exist_ok=True)
            with open(os.path.join(tmpdir, fname), 'w') as f:
                f.write(value)
    proc = Popen(args, stdin=PIPE, stdout=PIPE, stderr=PIPE, env=env,
                 shell=shell, cwd=tmpdir)
    stdout, stderr = proc.communicate(stdin)
    _check_output(expected,
                  {'stdout': stdout.decode('UTF-8'),
                   'stderr': stderr.decode('UTF-8'),
                   'returncode': proc.returncode},
                  tmpdir)


def _check_output(expected, actual, tmpdir):
    """Check using an assertion if the actual values match expected.

    Arguments:
      `expected`: Expected values (dict or list(dict))
      `actual`: Actual values (dict)
      `tmpdir`: The temporary directory (containing output files)
    """
    for key, expected_vals in sorted(expected.items()):
        if key in actual:
            actual_val = actual[key]
        elif key.startswith('file:'):
            fname = os.path.join(tmpdir, key.split(':', maxsplit=1)[1])
            assert os.path.isfile(fname)
            with open(fname, 'r') as f:
                actual_val = f.read()
        if expected_vals is None:
            expected_vals = ['']
        elif not isinstance(expected_vals, list):
            expected_vals = [expected_vals]
        for expected_val in expected_vals:
            if isinstance(expected_val, dict):
                if 'test' in expected_val:
                    test, *opts = expected_val['test'].split()
                    if 'opts' in expected_val:
                        if isinstance(expected_val['opts'], list):
                            opts.extend(expected_val['opts'])
                        else:
                            opts.extend(expected_val['opts'].split())
                    assert _output_tests[test](
                        expected_val['value'], actual_val, *opts)
                else:
                    for test, exp_vals in expected_val.items():
                        test, *opts = test.split()
                        if not isinstance(exp_vals, list):
                            exp_vals = [exp_vals]
                        for exp_val in exp_vals:
                            assert _output_tests[test](
                                exp_val, actual_val, *opts)
            else:
                assert actual_val == expected_val
