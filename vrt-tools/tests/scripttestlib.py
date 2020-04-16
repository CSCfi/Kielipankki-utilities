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

from collections import defaultdict
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
            fname_rel = os.path.relpath(fname, basedir)
            if fname.endswith('.py'):
                # print(basedir, sys.path)
                testcases.append(
                    (fname_rel,
                     importlib.import_module(os.path.basename(fname)[:-3])
                     .testcases))
            elif fname.endswith(('.yaml', '.yml')):
                with open(fname, 'r') as yf:
                    testcases.append(
                        (fname_rel, [item for items in yaml.safe_load_all(yf)
                                     for item in items]))
    return expand_testcases(testcases)


def expand_testcases(fname_testcases_dictlist):
    """Convert a list of (filename, test case dict) to a list of tuples."""

    testcases = []
    default_values = {}

    def get_output_value(d):
        return d.get('output') or d.get('expected', {})

    def get_value(default_val, base_val):
        return (dict_deep_update(dict(default_val), base_val) if default_val
                else base_val)

    # print(fname_testcases_dictlist)
    for fname, testcases_dictlist in fname_testcases_dictlist:
        default_input = {}
        default_output = {}
        default_status = None
        for tcnum, tc in enumerate(testcases_dictlist):
            if 'defaults' in tc:
                # New defaults override (are merged to) possibly existing
                # defaults
                defaults = tc['defaults']
                default_input = dict_deep_update(
                    default_input, defaults.get('input'))
                default_output = dict_deep_update(
                    default_output, get_output_value(defaults))
                default_status = defaults.get('status')
                continue
            if 'input' not in tc:
                continue
            params = ('{} {:d}: {}'.format(fname, tcnum + 1,
                                           tc.get('name', '')),
                      get_value(default_input, tc.get('input', {})),
                      get_value(default_output, get_output_value(tc)))
            # If status starts with "xfail", "skip" or "skipif", mark the test
            # accordingly.
            status_value = tc.get('status') or default_status
            if status_value:
                status, _, reason = status_value.partition(':')
                reason = reason.strip() or None
                if status == 'skipif':
                    mark = pytest.mark.skipif(reason)
                elif status in ('skip', 'xfail'):
                    mark = getattr(pytest.mark, status)(reason=reason)
                testcases.append(pytest.param(*params, marks=mark))
            else:
                testcases.append(params)
    return testcases


def dict_deep_update(a, b):
    """Recursively update dict `a` from dict `b`.
    In cases of conflict, values in `b` override those in `a`.
    Returns updated `a`.
    Note that contents are not copied deeply, so the result typically
    contains references to parts of `b`. This needs to be kept in mind
    if modifying the result.
    Simplified from https://stackoverflow.com/a/7205107
    """
    if b and isinstance(b, dict) and isinstance(a, dict):
        for key in b:
            if (key in a and isinstance(a[key], dict)
                    and isinstance(b[key], dict)):
                a[key] = dict_deep_update(a[key], b[key])
            else:
                a[key] = b[key]
        return a
    return b


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
          `envvars`: a dict of environment variable values, added to
              or replacing values in the original environment. A value
              may reference other environment variables with `$VAR` or
              `${VAR}`, which is replaced by the value of `VAR`. A
              self-reference considers only the value in the original
              environment, whereas other references also consider the
              added or replaced values. A literal `$` is encoded as
              `$$`.
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
    # - Allow specifying input and output encodings.

    def update_env(env, new_vars):
        # Replace self-references with values from the original environment
        for var, value in new_vars.items():
            new_vars[var] = re.sub(
                r'(?<!\$)\$(?:' + var + r'\b|\{' + var + '\})',
                env.get(var, ''),
                value)
        env.update(new_vars)
        # Replace other references with values taking into account the new
        # values
        for var in new_vars:
            env[var] = re.sub(
                r'(?<!\$)\$(?:\w+|\{\w+\})',
                lambda mo: env.get(mo.group(0).strip('${}'), ''),
                env[var])
            # Replace double dollars with a single dollar
            env[var] = env[var].replace('$$', '$')
        return env

    shell = input_.get('shell', False)
    if 'cmdline' in input_:
        if not input_['cmdline']:
            raise ValueError('Empty cmdline in test "' + name + '"')
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
        elif args:
            prog = args[0]
        else:
            raise ValueError(
                'Missing or empty prog and args in test "' + name + '"')
    if 'envvars' in input_ or progpath is not None:
        env = dict(os.environ)
        if 'envvars' in input_:
            update_env(env, input_['envvars'])
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
    options = expected.get('options', {})
    if options:
        options = _process_output_options(options)
        del expected['options']
    _check_output(expected,
                  {'stdout': stdout.decode('UTF-8'),
                   'stderr': stderr.decode('UTF-8'),
                   'returncode': proc.returncode},
                  options,
                  tmpdir)


def _process_output_options(options_raw):
    """Split output option names to name and target

    If an output option name contains a space, the string following the
    space is considered the target (a subitem of "output", such as
    "stdout") to which the option is applied. Otherwise, the option is
    applied to all output items.

    Return `dict((target, list((optfunc, optval)))`: target "*" denotes
    any target; `optfunc` is mapped from option name via the dictionary
    `_output_option_funcs`.
    """
    options = defaultdict(list)
    for optname, optvals in options_raw.items():
        if ' ' in optname:
            optname, opttarget = optname.split(None, 2)
        else:
            opttarget = '*'
        optfunc = _output_option_funcs.get(optname)
        if optfunc is None:
            raise NameError('Unrecognized option name "' + optname + '"')
        if not isinstance(optvals, list):
            optvals = [optvals]
        options[opttarget].append((optfunc, optvals))
    return options


def _check_output(expected, actual, options, tmpdir):
    """Check using an assertion if the actual values match expected.

    Arguments:
      `expected`: Expected values (dict or list(dict))
      `actual`: Actual values (dict)
      `options`: Options for processing the actual values (dict)
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
        key_opts = options.get(key, [])
        key_opts.extend(options.get('*', []))
        for optfunc, optvals in key_opts:
            for optval in optvals:
                actual_val = optfunc(optval, actual_val)
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


def _outputopt_filter_out(opt_value, output_data):
    """Replace regexp `opt_value` matches with "" `in output_data`."""
    try:
        return re.sub(opt_value, '', output_data)
    except TypeError:
        return output_data


# Map output option names to functions
_output_option_funcs = {
    'filter-out': _outputopt_filter_out,
}
