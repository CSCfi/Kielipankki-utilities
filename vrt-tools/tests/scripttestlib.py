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
    input_trans = input_.get('transform', [])
    stdin = (_make_value(input_.get('stdin', ''), 'transform', input_trans)
             .encode('UTF-8'))
    for key, value in input_.items():
        if key.startswith('file:'):
            fname = key.split(':', maxsplit=1)[1]
            dirname = os.path.dirname(fname)
            if dirname:
                os.makedirs(os.path.join(tmpdir, dirname), exist_ok=True)
            with open(os.path.join(tmpdir, fname), 'w') as f:
                f.write(_make_value(value, 'transform', input_trans))
    proc = Popen(args, stdin=PIPE, stdout=PIPE, stderr=PIPE, env=env,
                 shell=shell, cwd=tmpdir)
    stdout, stderr = proc.communicate(stdin)
    _check_output(expected,
                  {'stdout': stdout.decode('UTF-8'),
                   'stderr': stderr.decode('UTF-8'),
                   'returncode': proc.returncode},
                  tmpdir)


def _make_value(value, trans_key, global_trans=None, actual_value=None):
    """Apply possible transformations to value.

    value is the literal value or a dict containing key "value" and
    possible transformations. trans_key is the key in value dict whose
    transformations should be retrieved. global_trans is a dictionary
    of global transformations (affecting all inputs or outputs) to be
    applied before the local ones. actual_value overrides value: it is
    used when processing actual values, whose transformations are
    defined in the expected value (as actual values cannot be present in
    the test case).
    """
    # print('_make_value', repr(value), trans_key, global_trans, repr(actual_value))
    trans_value = None
    trans = None
    if isinstance(value, dict):
        trans = value.get(trans_key)
        if actual_value is not None:
            trans_value = actual_value
        elif 'value' not in value:
            raise ValueError('Missing key "value"')
        else:
            trans_value = value.get('value')
    elif actual_value is not None:
        trans_value = actual_value
    else:
        trans_value = value
    trans_value = _transform_value(trans_value, global_trans)
    trans_value = _transform_value(trans_value, trans)
    return trans_value


def _transform_value(value, trans):
    """Return value transformed according to trans.

    trans is a dict whose keys KEY should correspond to functions
    _transform_value_KEY.
    """
    # print('_transform_value', repr(value), repr(trans))
    if not trans:
        return value
    # Convert a dict to a list of single-item dicts
    if isinstance(trans, dict):
        trans = (dict([(key, val)]) for key, val in trans.items())
    for transitem in trans:
        for transname, transval in transitem.items():
            # print(transname, transval)
            try:
                transfunc = globals()['_transform_value_'
                                      + transname.replace('-', '_')]
            except KeyError as e:
                raise ValueError('Unknown transformation "' + transname + '"')
            value = transfunc(value, transval)
    # print('->', repr(value))
    return value


def _check_output(expected, actual, tmpdir):
    """Check using an assertion if the actual values match expected.

    Arguments:
      `expected`: Expected values (dict or list(dict))
      `actual`: Actual values (dict)
      `tmpdir`: The temporary directory (containing output files)
    """
    expected_trans = expected.get('transform-expected', [])
    actual_trans = expected.get('transform-actual', [])

    def make_values(exp, act):
        # print('make_values', repr(exp), repr(act))
        return (_make_value(exp, 'transform-expected', expected_trans),
                _make_value(exp, 'transform-actual', actual_trans, act))

    def test_values(test, expected, actual, item_descr, *test_opts):
        exp_val, act_val = make_values(expected, actual)
        _assert(test, exp_val, act_val, item_descr, *test_opts)

    for key, expected_vals in sorted(expected.items()):
        if key in actual:
            actual_val = actual[key]
        elif key.startswith('file:'):
            fname = os.path.join(tmpdir, key.split(':', maxsplit=1)[1])
            assert os.path.isfile(fname)
            with open(fname, 'r') as f:
                actual_val = f.read()
        else:
            continue
        if expected_vals is None:
            expected_vals = ['']
        elif not isinstance(expected_vals, list):
            expected_vals = [expected_vals]
        for expected_val_num, expected_val in enumerate(expected_vals):
            item_descr = key + ' ' + str(expected_val_num + 1)
            if isinstance(expected_val, dict):
                if 'value' in expected_val:
                    test = expected_val.get('test', '==')
                    test, *test_opts = test.split()
                    reflags = expected_val.get('reflags', '')
                    if isinstance(reflags, list):
                        test_opts.extend(reflags)
                    else:
                        test_opts.extend(reflags.split())
                    test_values(test, expected_val, actual_val, item_descr,
                                *test_opts)
                else:
                    test_num = 0
                    for test, exp_vals in expected_val.items():
                        test_num += 1
                        test, *test_opts = test.split()
                        if not isinstance(exp_vals, list):
                            exp_vals = [exp_vals]
                        for exp_val_num, exp_val in enumerate(exp_vals):
                            test_values(test, exp_val, actual_val,
                                        ' '.join([item_descr, str(test_num),
                                                  str(exp_val_num + 1)]),
                                        *test_opts)
            else:
                test_values('==', expected_val, actual_val, item_descr, [])


def _re_search(patt, val, flags=''):
    """Wrap re.search: Flags as a string (re. prefixes can be omitted)."""
    if flags:
        flags = eval('|'.join(
            ('re.' if not flag.startswith('re.') else '') + flag
            for flag in flags.split('|')))
    return re.search(patt, val, flags=(flags or 0))


# Map test names to assertion function names (following _assert_)
_assert_name_map = {
    '==': 'equal',
    '!=': 'not_equal',
    '<': 'less',
    '<=': 'less_equal',
    '>': 'greater',
    '>=': 'greater_equal',
    'matches': 'regex',
    'not_matches': 'not_regex',
}


def _assert(test_name, expected, actual, *opts):
    """Call the assertion function corresponding to test_name with the args."""
    test_name_orig = test_name
    # Replace hyphens with underscores in the test name. The test name cannot
    # contain spaces, as space is used to separate options from the test name.
    test_name = test_name.replace('-', '_')
    test_name = _assert_name_map.get(test_name, test_name)
    try:
        globals()['_assert_' + test_name](expected, actual, *opts)
    except KeyError:
        raise ValueError('Unknown test "' + test_name_orig + '"')


# Assertion functions: the first argument is the expected and the second the
# actual value. item_descr describes the test item; it is not used in the
# functions but it shows up in pytest traceback providing more information on
# the exact test within a single test case. *opts may be used to pass options
# to the function, such as regular expression flags.

def _assert_equal(exp, val, item_descr, *opts):
    # This order or values makes the pytest value diff more natural
    assert exp == val

def _assert_not_equal(exp, val, item_descr, *opts):
    # This order or values makes the pytest value diff more natural
    assert exp != val

def _assert_less(exp, val, item_descr, *opts):
    assert val < exp

def _assert_less_equal(exp, val, item_descr, *opts):
    assert val <= exp

def _assert_greater(exp, val, item_descr, *opts):
    assert val > exp

def _assert_greater_equal(exp, val, item_descr, *opts):
    assert val >= exp

def _assert_in(exp, val, item_descr, *opts):
    assert val in exp

def _assert_not_in(exp, val, item_descr, *opts):
    assert val not in exp

def _assert_regex(exp, val, item_descr, *opts):
    assert _re_search(exp, val, *opts) is not None

def _assert_not_regex(exp, val, item_descr, *opts):
    assert _re_search(exp, val, *opts) is None


# Value transformation functions

def _transform_value_prepend(value, prepend_value):
    """Return value with prepend_value prepended."""
    return prepend_value + value


def _transform_value_append(value, append_value):
    """Return value with append_value appended."""
    return value + append_value


def _transform_value_filter_out(value, regexps):
    """Replace regexp `regexp` matches with "" `in `value`."""
    if not isinstance(regexps, list):
        regexps = [regexps]
    for regexp in regexps:
        try:
            value = re.sub(regexp, '', value)
        except TypeError:
            pass
    return value


def _transform_value_python(value, code):
    """Return value transformed with Python code (function body)."""
    funcdef = ('def transfunc(value):\n '
               + re.sub(r'^', '    ', code, flags=re.MULTILINE))
    exec(funcdef, globals())
    return transfunc(value)


def _transform_value_shell(value, code):
    """Return value transformed with shell commands code."""
    proc = Popen(code, stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True)
    stdout, stderr = proc.communicate(value.encode('UTF-8'))
    return stdout.decode('UTF-8')
