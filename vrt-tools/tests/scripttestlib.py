#! /usr/bin/env python3


"""
scripttestlib.py

A module for processing tests of complete scripts, for running with
pytest.

Please see README.md and the docstrings of functions for more
information.
"""


# TODO:
# - Support overriding "status" (xfail, skip, skipif) in a grouped
#   transformation and in an individual test specified as a dict.


import glob
import importlib
import os
import os.path
import re
import shlex
import sys

from collections import defaultdict
from copy import deepcopy
from itertools import product
from subprocess import Popen, PIPE

import pytest
import yaml


# Scripttest granularity: one of "value", "outputitem" or "programrun"; see the
# help text in add_pytest_option_scripttest_granularity for more information.
_option_scripttest_granularity = 'value'


def add_pytest_option_scripttest_granularity(parser):
    """Add custom option --scripttest-granularity to pytest option parser."""
    parser.addoption(
        '--scripttest-granularity',
        choices=['value', 'outputitem', 'programrun'], default='value',
        help="""
            parametrize scripttestlib tests at the given granularity,
            indicating what is made a pytest test of its own (from
            finest to coarsest): "value" (each value to be tested is
            made its own test), "outputitem" (each output item of a
            program run) or "programrun" (each program run) (default:
            "%(default)s")
        """
        )


def set_scripttest_granularity(granularity):
    """Set scripttest granularity to one of {value, outputitem, programrun}."""
    global _option_scripttest_granularity
    _option_scripttest_granularity = granularity


def _get_granularity():
    """Return the value of the custom --scripttest-granularity option"""
    return _option_scripttest_granularity


def make_param_id(val):
    """Return a parameter id string for value `val`

    To be used as the value of the `ids` argument of
    `pytest.mark.parametrize` for generating more readable parameter
    values in test ids.
    """
    # If all values of a list or tuple are the same, use only one of them
    if (isinstance(val, (list, tuple))
            and all(item == val[0] for item in val[1:])):
        val = val[0]
    if isinstance(val, dict) and 'value' in val and 'test' in val:
        # Generate a more readable representation for the expected value
        value = val['value']
        if isinstance(value, (int, bool)) or value is None:
            value = str(value)
        if not isinstance(value, str):
            value = repr(value)
        # Abridge long values
        if len(value) > 80:
            value = value[:60] + '[...]' + value[-20:]
        return val['test'] + ':' + value
    return val if isinstance(val, str) else None


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
        elif add is None or isinstance(add, (str, int)):
            add = [add]
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

    def make_subcases(fname, tc, tcnum, default_input, default_output):
        """Generate sub-testcases, expanding inputs and output.

        Generate sub-testcases for testcase `tc` (number `tcnum`) in
        file `fname`, with defaults `default_input` and
        `default_output`. If the input specification is a list, each
        item in it generates a separate test for each test case in the
        output. The return value is a list of tuples to be used as
        parameters to `check_program_run`.
        """
        inputs = tc.get('input')
        if not isinstance(inputs, list):
            inputs = [inputs]
        inputs = expand_inputs(inputs)
        # Name format depends on whether the input is a list or not
        name_format = ('{fname} {num:d}: {name}' if len(inputs) == 1
                       else '{fname} {num:d}.{inputnum:d}: {name}')
        # print(tcnum, inputs)
        subcases = []
        tcname = tc.get('name') or ''
        for inputnum, input_ in enumerate(inputs):
            # print(tcname, inputnum, input_, file=sys.stderr)
            _convert_files_dict(input_, 'input')
            inputname = (input_ or {}).get('name') or ''
            input_ = get_value(default_input, input_)
            output = get_value(default_output, get_output_value(tc))
            _convert_files_dict(output, 'output')
            input_output = [(input_, output)]
            if 'transform' in tc:
                # Expand grouped transformations
                input_output = expand_grouped_transforms(
                    input_output, tc['transform'])
                name_format = name_format.replace('}:', '}:{transnum:d}:')
            # print('name_format', name_format)
            for trnum, input_output_item in enumerate(input_output):
                real_input, real_output = input_output_item[0:2]
                transname = (
                    ': ' + input_output_item[2] if len(input_output_item) > 2
                    else '')
                subcase_name = (
                    tcname
                    + (f' ({inputname})' if inputname else '')
                    + (f' (transform {trnum + 1}{transname})'
                       if 'transform' in tc else ''))
                full_name = name_format.format(
                    fname=fname, num=tcnum + 1, inputnum=inputnum + 1,
                    transnum=trnum + 1, name=subcase_name)
                subcases.extend(make_output_subcases(
                    full_name, real_input, real_output))
        return subcases

    def expand_inputs(inputs):
        """Expand `inputs`: all item combinations of list-valued values.

        Return a list of input dicts generated from each item of
        `inputs` so that the result contains each combination (element
        of cross-product) of items of list-valued values.

        For example, `{cmdline: [c1, c2], stdin: [s1, s2]}` becomes
        `[{cmdline: c1, stdin: s1}, {cmdline: c1, stdin: s2},
        {cmdline: c2, stdin: s1}, {cmdline: c2, stdin: s2}]`.
        """
        # The keys whose values are not expanded
        exclude_keys = {'name', 'args', 'shell', 'transform'}
        expanded = []
        for input_ in inputs:
            # input_ may be None
            if not input_:
                continue
            # Keys whose values should be expanded
            expand_keys = [
                key for key, val in input_.items()
                if key not in exclude_keys and isinstance(val, list)]
            if expand_keys:
                expanded.extend(expand_input(input_, expand_keys))
            else:
                expanded.append(input_)
        return expanded

    def expand_input(input_, expand_keys):
        """Expand `input_`: return all item combinations of `expand_keys`.

        Return a list of copies of `input_` dict with one copy for
        each combination of items in the value lists of keys
        `expand_keys`.
        """
        expanded = []
        # Cross product containing tuples for all combinations of
        # indices for the values of keys in expand_keys in input_
        value_indices_iter = product(*(range(len(input_[key]))
                                       for key in expand_keys))
        for value_indices in value_indices_iter:
            # Tuple containing the actual values corresponding to
            # indices in value_indices
            values = tuple(input_[expand_keys[keynum]][index]
                           for keynum, index in enumerate(value_indices))
            expanded.append(make_input_item(input_, expand_keys,
                                            values, value_indices))
        return expanded

    def make_input_item(input_, expand_keys, values, value_indices):
        """Make and return a single input item from the arguments.

        Return a deep copy of `input_` dict with the values of keys
        listed in `expand_keys` replaced with values in tuple `values`
        (whose values are in the same order as key names in
        `expand_keys`. `value_indices` is a list of indices indicating
        the index of each value in `values` in the original list value
        in the input; it is used to add or append to the `name` of the
        input.
        """
        result = deepcopy(input_)
        # print('make_input_item', input_, values, expand_keys)
        for i, value in enumerate(values):
            # CHECK: Should we make a deep copy of value, too?
            result[expand_keys[i]] = value
            # print(i, value, expand_keys[i], result)
        # Generate a list "key1 i1, key2 i2, ..." for the expanded
        # keys and value indices, to be added as (or appended to) name
        name = ', '.join(expand_keys[keynum] + ' ' + str(index + 1)
                         for keynum, index in enumerate(value_indices))
        # If the input already has a name, append to it after a colon
        if 'name' in input_:
            name = result['name'] + ': ' + name
        result['name'] = name
        return result

    def make_output_subcases(name, input_, output):
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
            if expected_vals is None and not key.startswith('file:'):
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
                            # print('test', test, exp_vals)
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
                                # print(exp_val_num, exp_val, exp_output)
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

    def expand_grouped_transforms(input_outputs, transform_groups):
        """Expand grouped transformations `transform_groups` in `input_outputs`.

        Return `input_outputs` with a separate test generated for each
        input and output pair and transform group in
        `transform_groups`.

        `input_outputs` is a list of pairs (input, output): the input
        and its expected output.
        `transform_groups` is a list of dicts, each dict containing
        transformations to be applied to each (input, output) pair as
        a group. Such a dict may contain keys ``input``,
        ``output-expected`` and ``output-actual`` for adding
        transformations to input, expected output and actual output
        items.
        """
        result = []
        for input_, output in input_outputs:
            for transform_group in transform_groups:
                if transform_group:
                    result.append(
                        add_transform_group(input_, output, transform_group))
                else:
                    # If the transformation is empty, return input_
                    # and output as is
                    result.append((input_, output))
        return result

    def add_transform_group(input_, output, transform_group):
        """Return copy of [`input_`, `output`] with `transform_group` added.

        Add to a deep copy of `input_` and `output` the applicable
        transformations in `transform_group` and return them as list
        of pairs or triples (lists). (The optional third item is the
        value of the ``name`` of the transformation group.)`input_`
        and `output` correspond to the dicts ``input`` and ``output``
        in a scripttestlib test.
        """
        result = [deepcopy(input_), deepcopy(output)]
        # Input and output top targets
        target_tops = {'input': result[0], 'output': result[1]}
        # print('add_transform_group', result, transform_group)
        # transform_group is a dict that may contain keys "input",
        # "output-expected", "output-actual", "name"
        for transform_top_name, transform_top in transform_group.items():
            if transform_top_name == 'name':
                result.append(transform_top)
                continue
            # target_top is "input" or "output"
            target_top, sep, kind = transform_top_name.partition('-')
            # The key for these transformations in input_ or output:
            # "transform", "transform-expected" or "transform-actual"
            transform_key = f'transform{sep}{kind}'
            # Convert files: {FILE: ...} to file:FILE
            _convert_files_dict(transform_top,
                                'transform:' + transform_top_name)
            # print(transform_top_name, target_top, transform_key,
            #       transform_top)
            # target is test target (stdin, stdout, file, returncode),
            # transform_item the transform to be applied to it
            for target, transform_item in transform_top.items():
                # print(transform_key, target, transform_group,
                #       transform_item, result)
                # Add the transformation; if the target item does not
                # exist, default to None (non-existing)
                target_tops[target_top][target] = add_new_transform(
                    target_tops[target_top].get(target, {'value': None}),
                    transform_key, transform_item)
        # print('add_transform_group ->', result)
        return result

    def add_new_transform(target, transform_key, transform_items):
        """Append `transform_items` to `transform_key` of `target`.

        Append transformations in `transform_items` to the
        transformation type `transform_key` of `target` whose value is
        to be tested. `transformation_items` can be a dict or a list
        of dicts. Return `target` with the transformation appended.
        """
        # print("add_new_transform", transform_key, target, transform_items)
        if isinstance(target, list):
            return [add_new_transform(subtarget, transform_key, transform_items)
                    for subtarget in target]
        elif isinstance(target, dict):
            if 'value' in target:
                target.setdefault(transform_key, [])
                if isinstance(target[transform_key], dict):
                    target[transform_key] = [target[transform_key]]
            elif 'transform-expected' in target or 'transform-actual' in target:
                # Return test-specific transformations (a
                # transformation dict within a list) intact
                return target
            else:
                # Dict with test names as keys
                result = []
                for test_name, test_vals in target.items():
                    if test_name in _test_names:
                        # The value can be a list of values to test
                        if not isinstance(test_vals, list):
                            test_vals = [test_vals]
                        for test_val in test_vals:
                            result.append(add_new_transform(
                                {
                                    'test': test_name,
                                    'value': test_val,
                                },
                                transform_key, transform_items))
                return result
        elif isinstance(target, (str, int)):
            # If target is not a dict, convert it to one, with the
            # original value as the value of key 'value'
            target = {
                'value': target,
                transform_key: [],
            }
        else:
            # print(target, transform_key, transform_items)
            raise ValueError(
                'Grouped transformations currently work only with string'
                ' values and dicts with key "value": ' + repr(target))
        if not isinstance(transform_items, list):
            transform_items = [transform_items]
        for transform_item in transform_items:
            target[transform_key].append(transform_item)
        # print("added", target)
        return target

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
            subcases = make_subcases(fname, tc, tcnum,
                                     default_input, default_output)
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


def _convert_files_dict(d, type_):
    """Convert files: {fname: ...} to file:fname: ... in dict d of type_

    type_ is "input" or "output", used only in the error message"""
    if 'files' in d:
        for fname, value in d['files'].items():
            if ('file:' + fname) in d:
                raise ValueError(
                    ('Value for {type} file {fname} specified both as'
                     ' file:{fname} and as files: {{{fname}}}').format(
                         fname=fname, type=type_))
            d['file:' + fname] = value
        del d['files']


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

        def __init__(self, val, tmpdir='', env=None):
            """Initialize with the dict `val`, files in `tmpdir`, env `env`."""
            super().__init__()
            if isinstance(val, dict):
                self.update(val)
            self.tmpdir = tmpdir
            self.env = env

        def get(self, key, default=None):
            """Like dict.get, but with special treatment of keys "file:FNAME"

            If `key` is of the form "file:FNAME", return the content
            of the file ``FNAME`` in `self.tmpdir`, or `None` if
            ``FNAME`` does not exist.
            """
            if key in self:
                return self[key]
            elif key.startswith('file:'):
                fname = os.path.join(
                    self.tmpdir, key.split(':', maxsplit=1)[1])
                if not os.path.isfile(fname):
                    return None
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

        def get_prog_args(input_):
            shell = input_.get('shell', False)
            if 'cmdline' in input_:
                # Complete command line
                cmdline = _make_value(input_['cmdline'], 'transform')
                if not cmdline:
                    raise ValueError('Empty cmdline in test "' + name + '"')
                if shell:
                    args = cmdline
                    prog = None
                else:
                    args = shlex.split(cmdline)
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
            return prog, args, shell

        def make_env(input_):
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
            return env

        def update_env(env, new_vars):
            # Replace self-references with values from the original environment
            for var, value in new_vars.items():
                new_vars[var] = re.sub(
                    r'(?<!\$)\$(?:' + var + r'\b|\{' + var + r'\})',
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

        def create_files(input_):
            input_trans = input_.get('transform', [])
            stdin = (_make_value(input_.get('stdin', ''), 'transform',
                                 input_trans)
                     .encode('UTF-8'))
            # Create input files
            for key, value in input_.items():
                if key.startswith('file:'):
                    fname = key.split(':', maxsplit=1)[1]
                    dirname = os.path.dirname(fname)
                    if dirname:
                        os.makedirs(os.path.join(tmpdir, dirname),
                                    exist_ok=True)
                    # print('create_files 0', key, value)
                    value = _make_value(value, 'transform', input_trans)
                    # print('create_files 1', key, value)
                    if value is not None:
                        with open(os.path.join(tmpdir, fname), 'w') as f:
                            f.write(value)
            return stdin

        if input_ == cls._input:
            return cls._output
        cls._input = input_
        # print(input_, expected)
        prog, args, shell = get_prog_args(input_)
        env = make_env(input_)
        stdin = create_files(input_)
        # Run the command
        # print('running', args)
        proc = Popen(args, stdin=PIPE, stdout=PIPE, stderr=PIPE, env=env,
                     shell=shell, cwd=tmpdir)
        stdout, stderr = proc.communicate(stdin)
        cls._output = cls._Output({
            'stdout': stdout.decode('UTF-8'),
            'stderr': stderr.decode('UTF-8'),
            'returncode': proc.returncode,
        }, tmpdir=tmpdir, env=env)
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

    # print("run", input_, outputitem, expected)
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
    # print('_make_value before transform', repr(trans_value))
    trans_value = _transform_value(trans_value, global_trans)
    trans_value = _transform_value(trans_value, trans)
    # print('_make_value after transform', repr(trans_value))
    return trans_value


def _transform_value(value, trans, tmpdir=None, env=None):
    """Return value transformed according to trans.

    `trans` is a `dict` whose keys ``KEY`` should correspond to
    functions `_transform_value_KEY` (hyphens in ``KEY`` converted to
    underscores). `tmpdir` is the directory containing output files,
    `env` a dict containing environment variables (may be used in
    shell transformations).

    Functions `_transform_value_KEY` should return the value intact if
    the transformation is not applicable to the type of the value.
    """
    # print('_transform_value', repr(value), repr(trans))
    if not trans:
        return value
    # Convert a dict to a list of single-item dicts
    if isinstance(trans, dict):
        trans = [dict([(key, val)]) for key, val in trans.items()]
    # str or int is converted to a list containing the value
    elif isinstance(trans, (str, int)):
        trans = [trans]
    # If value is a list, transform each item separately
    if isinstance(value, list):
        return [_transform_value(item, trans) for item in value]
    for transitem in trans:
        # If the transformation item is not a dict, treat the value as
        # the complete new value
        if not isinstance(transitem, dict):
            transitem = {'set-value': transitem}
        for transname, transval in transitem.items():
            # print(transname, transval)
            try:
                transfunc = globals()['_transform_value_'
                                      + transname.replace('-', '_')]
            except KeyError as e:
                raise ValueError('Unknown transformation "' + transname + '"')
            value = transfunc(value, transval, tmpdir=tmpdir, env=env)
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
    # print('_check_output', name, output, outputitem, expected, actual)
    tmpdir = output.tmpdir
    env = output.env
    exp_val = _transform_value(
        expected.get('value'), expected.get('transform-expected'), tmpdir, env)
    act_val = _transform_value(
        actual, expected.get('transform-actual'), tmpdir, env)
    # print('_check_output', repr(expected), repr(actual),
    #       repr(exp_val), repr(act_val))
    _assert(expected.get('test'), exp_val, act_val, name,
            opts=expected.get('test-opts'))


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


def _assert(test_name, expected, actual, item_descr, **kwargs):
    """Call the assertion function corresponding to test_name with the args."""
    test_name_orig = test_name
    # Replace hyphens with underscores in the test name. The test name cannot
    # contain spaces, as space is used to separate options from the test name.
    test_name = test_name.replace('-', '_')
    test_name = _assert_name_map.get(test_name, test_name)
    try:
        globals()['_assert_' + test_name](expected, actual, item_descr,
                                          **kwargs)
    except KeyError:
        raise ValueError('Unknown test "' + test_name_orig + '"')


# Assertion functions: the first argument is the expected and the second the
# actual value. item_descr describes the test item; it is not used in the
# functions but it shows up in pytest traceback providing more information on
# the exact test within a single test case. **kwargs is used to pass
# information to functions that is not needed by all: 'opts' may be used to
# pass options to the function, such as regular expression flags.

def _assert_equal(exp, val, item_descr, **kwargs):
    # This order or values makes the pytest value diff more natural
    assert exp == val

def _assert_not_equal(exp, val, item_descr, **kwargs):
    # This order or values makes the pytest value diff more natural
    assert exp != val

def _assert_less(exp, val, item_descr, **kwargs):
    assert val < exp

def _assert_less_equal(exp, val, item_descr, **kwargs):
    assert val <= exp

def _assert_greater(exp, val, item_descr, **kwargs):
    assert val > exp

def _assert_greater_equal(exp, val, item_descr, **kwargs):
    assert val >= exp

def _assert_in(exp, val, item_descr, **kwargs):
    assert val in exp

def _assert_not_in(exp, val, item_descr, **kwargs):
    assert val not in exp

def _assert_contains(exp, val, item_descr, **kwargs):
    assert exp in val

def _assert_not_contains(exp, val, item_descr, **kwargs):
    assert exp not in val

def _assert_regex(exp, val, item_descr, **kwargs):
    assert _re_search(exp, val, kwargs.get('opts')) is not None

def _assert_not_regex(exp, val, item_descr, **kwargs):
    assert _re_search(exp, val, kwargs.get('opts')) is None



# Supported test names
_test_names = set(
    list(name[len('_assert_'):] for name in dir()
         if name.startswith('_assert_'))
    + list(_assert_name_map.keys()))


# Value transformation functions

def _transform_value_prepend(value, prepend_value, **kwargs):
    """Return value with prepend_value prepended."""
    if value is None:
        value = ''
    elif not isinstance(value, str):
        return value
    return prepend_value + value


def _transform_value_append(value, append_value, **kwargs):
    """Return value with append_value appended."""
    if value is None:
        value = ''
    elif not isinstance(value, str):
        return value
    return value + append_value


def _transform_value_set_value(value, new_value, **kwargs):
    """Return `new_value`, discarding `value` if they have the same type."""
    return (new_value if isinstance(value, int) == isinstance(new_value, int)
            else value)


def _transform_value_filter_out(value, regexps, **kwargs):
    """Replace regexp `regexp` matches with "" `in `value`."""
    if not isinstance(value, str):
        return value
    if not isinstance(regexps, list):
        regexps = [regexps]
    for regexp in regexps:
        try:
            value = re.sub(regexp, '', value)
        except TypeError:
            pass
    return value


def _transform_value_replace(value, args, **kwargs):
    """Replace strings or regular expression matches in `value`.

    `args` can be a `dict`, `str` or `list` of `dict` or `str`. A
    `dict` value may contain the following keys: either `"str"` for
    the string to be replaced or `"regex"` for a regular expression,
    `"with"` for the replacement string (empty string if omitted), and
    optionally `"count"` for the number of replacements (default:
    all). A `str` value is of the form `/regex/with/` replacing
    matches of regular expression `regex` with `with`. Instead of the
    slash, another punctuation character may be used. If `args` is a
    `list`, each item in the list is processed in order as above.
    """
    if not isinstance(value, str):
        return value
    if isinstance(args, list):
        for item in args:
            value = _transform_value_replace(value, item)
    elif isinstance(args, str):
        if args:
            parts = args[1:].split(args[0])
            if len(parts) == 1:
                parts.append('')
            value = re.sub(parts[0], parts[1], value)
    elif isinstance(args, dict):
        repl = args.get('with', '')
        count = int(args.get('count', 0))
        if 'str' in args:
            # For str.replace, -1 replaces all
            if count == 0:
                count = -1
            value = value.replace(args['str'], repl, count)
        elif 'regex' in args:
            value = re.sub(args['regex'], repl, value, count)
    return value


def _transform_value_python(value, code, **kwargs):
    """Return value transformed with Python code (function body)."""
    return _exec_python_func(code, value)


def _transform_value_shell(value, code, **kwargs):
    """Return value transformed with shell commands code."""
    if value is None:
        return value
    valuetype = type(value)
    value = _exec_shell(code, str(value), tmpdir=kwargs.get('tmpdir'),
                        env=kwargs.get('env'))
    return valuetype(value)


def _exec_python_func(code, value):
    """Execute Python code `code` (function body) with arg `value`."""
    funcdef = ('def func(value):\n '
               + re.sub(r'^', '    ', code, flags=re.MULTILINE))
    exec(funcdef, globals())
    return func(value)


def _exec_shell(code, stdin, tmpdir=None, env=None):
    """Execute shell `code` with `stdin` input in `tmpdir` with env `env`."""
    proc = Popen(code, stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True,
                 cwd=tmpdir, env=env)
    stdout, stderr = proc.communicate(stdin.encode('UTF-8'))
    return stdout.decode('UTF-8')
