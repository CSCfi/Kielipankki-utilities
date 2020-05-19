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
from copy import deepcopy
from subprocess import Popen, PIPE

import pytest
import yaml


def _get_granularity():
    """Return the value of the custom --scripttest-granularity option"""
    return pytest.config.getoption('--scripttest-granularity')


def collect_testcases(*filespecs, basedir=None, granularity=None):
    """Return a list of tuples for the test cases in `filespecs`

    Collect the test cases found in the files matching one of
    `filespecs` in the directory `basedir`. The test cases are either
    in Python modules in a variable named `testcases` or in YAML
    files.

    The output tuples have the items (name, input, outputitem,
    expected), and they can be used as parameters to
    `check_program_run`.

    In general, each item in the output tuples is a list or tuple,
    containing the values to be tested in a single pytest test,
    determined by `granularity`: ``value`` (each value to be tested is
    made its own test), ``outputitem`` (each output item of a program
    run) or ``programrunrun`` (each program run). If `granularity` is
    `None`, the value `_test_granularity` of the custom
    --scripttest-granularity command-line option is used. If all the
    values for name or input are the same in a tuple, the single value
    is used instead of the tuple.
    """
    if granularity is None:
        granularity = _get_granularity()
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
            # print(basedir, filespec, fname, fname_rel)
            if fname.endswith('.py'):
                modulename = os.path.basename(fname)[:-3]
                pkgname = os.path.dirname(fname_rel).replace('/', '.')
                if pkgname:
                    modulename = pkgname + '.' + modulename
                testcases.append(
                    (fname_rel,
                     importlib.import_module(modulename)
                     .testcases))
            elif fname.endswith(('.yaml', '.yml')):
                with open(fname, 'r') as yf:
                    testcases.append(
                        (fname_rel, [item for items in yaml.safe_load_all(yf)
                                     for item in items]))
    return expand_testcases(testcases, granularity=granularity)


def expand_testcases(fname_testcases_dictlist, granularity=None):
    """Convert a list of (filename, test case dict) to a list of tuples.

    The returned tuples have the items (name, input, outputitem,
    expected), and they can be used as parameters to
    `check_program_run`. `granularity` is the granularity of the
    generated pytest tests, as explained in `collect_testcases`.
    """

    if granularity is None:
        granularity = _get_granularity()
    testcases = []
    default_values = {}
    item_descr_format = {
        'value': '{name}: {key}{num}',
        'outputitem': '{name}: {key}',
        'programrun': '{name}',
        }[granularity]

    def get_output_value(d):
        return d.get('output', d.get('expected'))

    def get_value(default_val, base_val):
        if default_val:
            if base_val:
                # Make a deep copy of the default value so that overriding
                # defaults does not update the defaults themselves.
                return dict_deep_update(deepcopy(default_val), base_val)
            else:
                return default_val
        else:
            return base_val

    def add_transforms(base, add):
        """Append transforms `add` to the list `base`

        If `add` is a dictionary, append each key-value pair as a
        dictionary of its own.
        """
        # print('add_transforms', base, add)
        if isinstance(add, dict):
            add = [{key: val} for key, val in add.items()]
        base.extend(add)
        return base

    def make_subcase_tuple(subcases):
        """Convert a list of tuples to a tuple of lists (tuples)

        If all the values of the first or second item of the tuple are
        the same, make it a single value.
        """
        result = list(zip(*subcases))
        for i in range(2):
            if all(val == result[i][0] for val in result[i][1:]):
                result[i] = result[i][0]
        return result

    def make_subcases(name, input_, output):
        """Generate sub-testcases, expanding `output`

        Each test case in `output` becomes its own item, with the same
        base in `name` and the same `input_`. The return value is a
        list of tuples to be used as parameters to
        `check_program_run`.
        """
        # print('make_subcases', name, input_, output)
        result = []
        subcases = []
        for key, expected_vals in sorted(output.items()):
            # Transformations are handled below
            if key.startswith('transform'):
                continue
            if expected_vals is None:
                expected_vals = ['']
            elif not isinstance(expected_vals, list):
                expected_vals = [expected_vals]
            # Reset the values for each file if file-specific transformations
            # had been appended
            expected_trans = add_transforms(
                [], output.get('transform-expected', []))
            actual_trans = add_transforms(
                [], output.get('transform-actual', []))
            # print('trans', expected_trans, actual_trans)
            expected_val_count = len(expected_vals)
            for expected_val_num, expected_val in enumerate(expected_vals):
                item_descr = item_descr_format.format(
                    name=name, key=key,
                    num=(' ' + str(expected_val_num + 1)
                         if expected_val_count > 1 else ''))
                if isinstance(expected_val, dict):
                    exp_trans = expected_val.get('transform-expected', [])
                    act_trans = expected_val.get('transform-actual', [])
                    if 'value' in expected_val:
                        test = expected_val.get('test', '==')
                        test, *test_opts = test.split()
                        reflags = expected_val.get('reflags', '')
                        if isinstance(reflags, list):
                            test_opts.extend(reflags)
                        else:
                            test_opts.extend(reflags.split())
                        exp_trans1 = expected_trans.copy()
                        act_trans1 = actual_trans.copy()
                        # print(exp_trans1, exp_trans, act_trans1, act_trans)
                        add_transforms(exp_trans1, exp_trans)
                        add_transforms(act_trans1, act_trans)
                        # print(exp_trans1, act_trans1)
                        # exp_trans1 = expected_trans.copy()
                        # exp_trans1.extend(exp_trans)
                        # act_trans1 = actual_trans.copy()
                        # act_trans1.extend(act_trans)
                        exp_output = {
                            'value': expected_val['value'],
                            'test': test,
                            'test-opts': test_opts,
                            'transform-expected': exp_trans1,
                            'transform-actual': act_trans1,
                        }
                        subcases.append((item_descr, input_, key, exp_output))
                    elif exp_trans or act_trans:
                        # File-specific transformations are appended to the
                        # global ones for all subsequent tests for this file
                        add_transforms(expected_trans, exp_trans)
                        add_transforms(actual_trans, act_trans)
                    else:
                        test_num = 0
                        for test, exp_vals in expected_val.items():
                            test_num += 1
                            test, *test_opts = test.split()
                            if not isinstance(exp_vals, list):
                                exp_vals = [exp_vals]
                            for exp_val_num, exp_val in enumerate(exp_vals):
                                exp_output = {
                                    'value': exp_val,
                                    'test': test,
                                    'test-opts': test_opts,
                                    'transform-expected': expected_trans,
                                    'transform-actual': actual_trans,
                                }
                                subitem_descr = item_descr
                                if granularity == 'value':
                                    subitem_descr += ' ' + str(test_num)
                                subcases.append(
                                    (subitem_descr, input_, key, exp_output))
                else:
                    exp_output = {
                        'value': expected_val,
                        'test': '==',
                        'transform-expected': expected_trans,
                        'transform-actual': actual_trans,
                    }
                    subcases.append((item_descr, input_, key, exp_output))
            if subcases and granularity != 'programrun':
                if granularity == 'value':
                    result.extend(subcases)
                elif granularity == 'outputitem':
                    result.append(make_subcase_tuple(subcases))
                subcases = []
        if subcases and granularity == 'programrun':
            result.append(make_subcase_tuple(subcases))
        # print('return subcases:', len(result), result)
        # for i in range(len(result)):
        #     print(len(result[i]), result[i])
        # print(len(result))
        return result

    # print(fname_testcases_dictlist)
    for fname, testcases_dictlist in fname_testcases_dictlist:
        default_input = {}
        default_output = {}
        default_status = None
        for tcnum, tc in enumerate(testcases_dictlist):
            if 'defaults' in tc:
                # New defaults override (are merged to) possibly existing
                # defaults
                # print('Defaults:', tc['defaults'])
                defaults = tc['defaults']
                # If defaults is empty, clear both input and output; without
                # this, get for them would return None, so dict_deep_update
                # would not update the values.
                if defaults == {}:
                    defaults = {'input': {}, 'output': {}}
                    # print('Clear defaults')
                # print(default_input, end=' -> ')
                default_input = dict_deep_update(
                    default_input, defaults.get('input'))
                # print(default_input)
                # print(default_output, end=' -> ')
                default_output = dict_deep_update(
                    deepcopy(default_output), get_output_value(defaults))
                # print(default_output)
                default_status = defaults.get('status')
                continue
            if (('input' not in tc and not default_input)
                    or ('output' not in tc and not default_output)):
                continue
            subcases = make_subcases(
                '{} {:d}: {}'.format(fname, tcnum + 1, tc.get('name', '')),
                get_value(default_input, tc.get('input')),
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
                for subcase in subcases:
                    testcases.append(pytest.param(*subcase, marks=mark))
            else:
                for subcase in subcases:
                    testcases.append(subcase)
    # print(len(testcases))
    return testcases


def dict_deep_update(a, b):
    """Recursively update dict `a` from dict `b`.

    In cases of conflict, values in `b` override those in `a`, except
    that `None` in `b` does not override a value in `a`.
    Returns updated `a`.
    Note that contents are not copied deeply, so the result typically
    contains references to parts of `b`. This needs to be kept in mind
    if modifying the result.
    Simplified from https://stackoverflow.com/a/7205107
    """
    # print('dict_deep_update', a, b)
    if b and isinstance(b, dict) and isinstance(a, dict):
        for key in b:
            if (key in a and isinstance(a[key], dict)
                    and isinstance(b[key], dict)):
                a[key] = dict_deep_update(a[key], b[key])
            else:
                a[key] = b[key]
        return a
    return b if b is not None else a


def add_output_test(name, test_fn):
    """Add output test `name` and its binary boolean function `test_fn`."""
    _output_tests[name] = test_fn


class ProgramRunner:

    """
    Class for running an external program and caching the results
    """

    _input = None
    _output = None

    class _Output(dict):

        """
        Class wrapping the output of a program run
        """

        def __init__(self, val, tmpdir=''):
            """Initialize with the dict `val`, files in `tmpdir`"""
            super().__init__()
            if isinstance(val, dict):
                self.update(val)
            self._tmpdir = tmpdir

        def get(self, key, default=None):
            """Like dict.get, but with special treatment of keys "file:FNAME"

            If `key` is of the form "file:FNAME", return the content
            of the file ``FNAME`` in self._tmpdir.
            """
            if key in self:
                return self[key]
            elif key.startswith('file:'):
                fname = os.path.join(
                    self._tmpdir, key.split(':', maxsplit=1)[1])
                assert os.path.isfile(fname)
                with open(fname, 'r') as f:
                    value = f.read()
                return value
            return default

    @classmethod
    def run(cls, name, input_, tmpdir, progpath=None):
        """Run the program specified in `input_`

        The specification of `input_` is as for the scripttests in
        general: command line, environment variables, stdin and possible
        input file contents. The input and output files are located in
        `tmpdir`, and `progpath` is used as the program path. `name` is
        used only in error messages.

        Cache the output to cls._output. If the method is called with
        the same `input_` several times in a row, the cached value is
        returned instead of running the program again.
        """

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

        if input_ == cls._input:
            return cls._output
        cls._input = input_
        # print(input_, expected)
        shell = input_.get('shell', False)
        if 'cmdline' in input_:
            # Complete command line
            if not input_['cmdline']:
                raise ValueError('Empty cmdline in test "' + name + '"')
            if shell:
                args = input_['cmdline']
            else:
                args = shlex.split(input_['cmdline'])
                prog = args[0]
        else:
            # prog and/or args
            shell = False
            args = input_.get('args', [])
            args = shlex.split(args) if isinstance(args, str) else args
            prog = input_.get('prog')
            if prog:
                args[0:0] = [prog]
            elif args:
                # If args only, prog is args[0]
                prog = args[0]
            else:
                raise ValueError(
                    'Missing or empty prog and args in test "' + name + '"')
        # Update environment variables
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
        # Create input files
        for key, value in input_.items():
            if key.startswith('file:'):
                fname = key.split(':', maxsplit=1)[1]
                dirname = os.path.dirname(fname)
                if dirname:
                    os.makedirs(os.path.join(tmpdir, dirname), exist_ok=True)
                with open(os.path.join(tmpdir, fname), 'w') as f:
                    f.write(_make_value(value, 'transform', input_trans))
        # Run the command
        proc = Popen(args, stdin=PIPE, stdout=PIPE, stderr=PIPE, env=env,
                     shell=shell, cwd=tmpdir)
        stdout, stderr = proc.communicate(stdin)
        cls._output = cls._Output({
            'stdout': stdout.decode('UTF-8'),
            'stderr': stderr.decode('UTF-8'),
            'returncode': proc.returncode,
        }, tmpdir=tmpdir)
        return cls._output


def check_program_run(name, input_, outputitem, expected, tmpdir,
                      progpath=None):
    """Check a program run: execute a single test case.

    Arguments:
      `name`: A name or description of the test (str)
      `input_`: A dict containing input information for the test
      `outputitem`: The output item to be tested (str)
      `expected`: The expected output for the test and associated
          information (dict):
         ``value``: the actual expected value (str or int, or list for
             tests ``in`` and ``not-in``)
         ``test``: the test condition (str)
         ``test-opts``: test condition options (list): currently
             only regular expression flags
         ``transform-expected``: transformations to be applied to the
             expected value (list(dict))
         ``transform-actual` : transformations to be applied to the
             actual output value (list(dict))
      `tmpdir`: The temporary directory in which to run the tests (the
          working directory for the commands and the base directory for
          input and output files)
      `progpath`: The directory or directories from which to search
          for the programs (scripts) to be run. Multiple directories are
          separated with colons and `{PATH}` is replaced with the current
          value of `$PATH`. If None, use the current `$PATH`.

    Alternatively, the values of `name`, `input_`, `outputitem` and
    `expected` may be lists or tuples containing information for tests
    grouped together. For `name` and `input`, all the values of a list
    or tuple are expected to be the same and only the first value is
    used.

    Please see README.md for more details on the values of `input_` and
    `expected` (output).

    All input and output is currently assumed to be encoded in UTF-8.
    """
    # TODO: Possible enhancements:
    # - Allow specifying input and output encodings.

    def is_list_or_tuple(value):
        return isinstance(value, list) or isinstance(value, tuple)

    def getfirst(value):
        return value[0] if is_list_or_tuple(value) else value

    output = ProgramRunner.run(
        getfirst(name), getfirst(input_), tmpdir, progpath)
    if not is_list_or_tuple(outputitem):
        outputitem = [outputitem]
        expected = [expected]
    for itemnum, outputitem_item in enumerate(outputitem):
        _check_output(name, output, outputitem_item, expected[itemnum])


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
    # print('_make_value', repr(value), trans_key, global_trans,
    #       repr(actual_value))
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
    if isinstance(trans_value, str):
        trans_value = _transform_value(trans_value, global_trans)
        trans_value = _transform_value(trans_value, trans)
    return trans_value


def _transform_value(value, trans):
    """Return value transformed according to trans.

    trans is a dict whose keys KEY should correspond to functions
    _transform_value_KEY.
    """
    # print('_transform_value', repr(value), repr(trans))
    if not isinstance(value, str) or not trans:
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


def _check_output(name, output, outputitem, expected):
    """Check using an assertion if the actual values match expected.

    Arguments:
      `name`: Test name
      `output`: Actual values (ProgramRunner._Output)
      `outputitem`: The output item to be tested (str)
      `expected`: Expected value, test condition and possible options,
          and possible transformations (dict)
    """
    actual = output.get(outputitem)
    exp_val = _transform_value(expected.get('value'),
                               expected.get('transform-expected'))
    act_val = _transform_value(actual, expected.get('transform-actual'))
    # print('_check_output', repr(expected), repr(actual),
    #       repr(exp_val), repr(act_val))
    _assert(expected.get('test'), exp_val, act_val, name,
            expected.get('test-opts'))


def _re_search(patt, val, flags=''):
    """Wrap re.search: Flags as a string (re. prefixes can be omitted)."""
    # print(patt, val, flags)
    if flags:
        if isinstance(flags, list):
            flags = '|'.join(flags)
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
