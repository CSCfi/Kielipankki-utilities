
# Tests for VRT Tools

This directory contains various tests for the FIN-CLARIN VRT Tools.


## Types of tests

The tests may take several different forms:

1.  Simple (shell) scripts that exit with code 0 if the test passes
    (or all the tests in the script pass) and with a non-zero exit
    code if the test fails (or some of the tests in the script fail).
    These are typically used for testing complete scripts.

2.  [pytest](https://docs.pytest.org/en/latest/) (or
    [unittest](https://docs.python.org/3/library/unittest.html) or
    [nose2](https://docs.nose2.io/en/latest/)) tests in Python files
    (modules) with names matching `test_*.py` or `*_test.py`. Please
    see the [pytest documentation](https://docs.pytest.org/en/latest/)
    for more information. pytest can be used for testing library
    functions (unit testing) as well as complete scripts.

3.  `scripttestlib` tests for complete scripts as either Python
    modules or [YAML](https://yaml.org/) files with the file name
    prefix `scripttest_`. This facility is based on pytest, using the
    Python module `scripttestlib` and the pytest test case
    `test_scripts.py` in this directory. Please see below for more
    information.


## `scripttestlib` tests

*(**Please note** that `scripttestlib` is not related to the
[scripttest library](https://github.com/pypa/scripttest), even though
they both help in testing command-line scripts.)*

`scripttestlib` allows specifying the input and expected output of a
script (shell command) as either (1) a Python data structure (a list
of dictionaries) named `testcases` in a Python module, or (2) a YAML
file with the same structure (a sequence of mappings), converted to
the Python data structure. You can also generate such a YAML file with
the `make-scripttest` script.


### The structure of a `scripttestlib` test

#### Test cases

A `scripttestlib` test contains the following information for a single
test case:

-   `name`: A name or description of the test (`str`)

-   `input`: A dict or a list of dicts containing input information
    for the test. If the value is a list of dicts, a separate test is
    generated for each item with the same output information.

    The input dict may contain the following keys:

    -   `name`: a name or description of the (sub-)test, mainly useful
        if `input` is a list of dicts, generating multiple tests
        (`str`)
    -   `prog`: program (script) name (`str`). The program is searched
        in `$PATH` as usual, but for tests under this directory, the
        `vrt-tools` directory is added to `$PATH`, so the bare name of
        the script can be used when testing VRT Tools scripts.
    -   `args`: a list of command-line arguments, either a single
        string with arguments quoted as in shell, or as a list of
        unquoted strings (`str`)
    -   `cmdline`: complete command line (`str` or `dict`; see below),
        with arguments quoted as in shell (an alternative to `prog`
        and `args`)
	-   `shell`: if `True`, pass `cmdline` to shell, allowing the use
        of pipes, redirection and other features. Note that this works
        only with `cmdline`, not with `prog` and `args`.
    -   `envvars`: a dict of environment variable values, added to or
        replacing values in the original environment. A value may
        reference other environment variables with `$VAR` or `${VAR}`,
        which is replaced by the value of `VAR`. A self-reference
        considers only the value in the original environment, whereas
        other references also consider the added or replaced values. A
        literal `$` is encoded as `$$`.
    -   `stdin`: the content of standard input (`str` or `dict`; see below)
    -   `file:FNAME`: the content of input file FNAME (`str` or
        `dict`; see below)
    -   `files`: a dict of input files with file names as keys and
        values as for `file:FNAME`. Both `files` and `file:FNAME` can
        be used, but each file must be specified only once.
    -   `transform`: transform the base content of standard input and
        all input files according to the specified options
        (`list(dict)`, `dict`, `str` or `int`). Currently the
        following options are supported:
		-   `prepend`: content to prepend to `value` (`str`); `None`
            is treated as an empty string, `int` returned intact
		-   `append`: content to append to `value` (`str`); `None`
            is treated as an empty string, `int` returned intact
		-   `filter-out`: remove the substrings matching the regular
			expression that is the value of the option. The value of
			the option may also be a list of regular expressions, in
			which case their matches are removed in order. `int` and
			`None` are returned intact.
        -   `replace`: replace a substring or regular expression match
            with a replacement. `int` and `None` are returned intact.
            The value can be a `dict`, `str` or
            `list` of `dict` or `str`. A `dict` value may contain the
            following keys (`str` and `regex` are mutually exclusive):
            -   `str`: fixed string to be replaced
            -   `regex`: regular expression whose matches are to be
                replaced
            -   `with`: replacement string (empty string if omitted);
                with regular expressions, may also refer to parts
                matching parenthesized groups as `\N` or `\g<N>` where
                _N_ is the number of the group in the regular
                expression, or to named groups (`(?P<name>regex)`) as
                `\g<name>`
            -   `count`: the number of replacements (optional;
                default: all)
            -   `reflags`: regular expression flags for `regex`. The
                value is as in Python, except that the names of the
                flag constants need not be prefixed by `re.`; e.g.,
                `DOTALL|VERBOSE` is the same as
                `re.DOTALL|re.VERBOSE`. Alternatively, the flags can
                be suffixed to the *key* `regex` following a space.

            A `str` value is of the form `/`_regex_`/`_with_`/`
            replacing matches of regular expression _regex_ with
            _with_. Instead of the slash, another punctuation
            character may be used. If the value is a `list`, its each
            item is processed in order as above.
        -   `set-value`: the value to replace `value` with completely.
            An `int` can only be replaced with an `int`, whereas
            `None` can replace `str` and vice versa; other type
            combinations return the original value intact.
		-   `python`: Python 3 code to transform `value`: the body of
            a function of one argument named `value` containing the
            base value and returning the transformed value. The Python
            regular expression module `re` is available for the code.
		-   `shell`: shell command line reading `value` from standard
            input and writing the transformed value to standard
            output. The shell used is the default shell. The command
            line is executed in the temporary directory containing the
            input and output files and with the environment variables
            specified in `envvars` of `input`. *Note* that the command
            should *not* change the input and output files, as their
            values may be cached for tests with the same input. An
            `int` `value` is converted to a string for processing and
            the returned value back to `int`; a `None` is returned
            intact.

		If the value is a plain dictionary, the order of the
        transformations is not defined, so they should be independent
        of each other. If the value is a list of single-item
        dictionaries, the transformations are applied in the list
        order, each transformation to the output of the preceding one.
        If the value is a plain `str` or `int`, or a list contains a
        plain `str` or `int` (or `None`), it is treated as replacing
        the value completely (implicit `set-value`).

	`cmdline`, `stdin`, `file:FNAME` and the values under `files` may
    be either plain strings containing the content, or dicts of one or
    two items:

	-   `value`: the base value (obligatory), subject to
        transformations specified in `transform` (`str`)
	-   `transform`: options for transforming the base value to the
        actual content. The options are those listed above for all
        inputs. If transformations are defined for both specific
        inputs and for all inputs, the input-specific transformations
        are applied after the general ones. (Transformations for all
        inputs do not apply to `cmdline`.)

	The dict variant of the input could be used in conjunction with
    [defining common values that can be reused in multiple
    places](#reusable-definitions), for example.

    For all keys except `name`, `args`, `shell` and `transform`, the
    value for the key may be a list of values of the indicated type,
    in which case separate tests are generated for each combination of
    list items. For example, `{cmdline: [c1, c2], stdin: [s1, s2]}`
    corresponds to inputs `[{cmdline: c1, stdin: s1}, {cmdline: c1,
    stdin: s2}, {cmdline: c2, stdin: s1}, {cmdline: c2, stdin: s2}]`

-   `output`: Expected output for the test and options transforming
    the output:
    -   `returncode`: program return code (`int`)
    -   `stdout`: the content of standard output (`str`, `dict` or
        `list`; see below)
    -   `stderr`: the content of standard error (`str`, `dict` or
        `list`; see below)
    -   `file:FNAME`: the content of file FNAME (`str`, `dict` or
        `list`; see below)
    -   `files`: a dict of output files with file names as keys and
        values as for `file:FNAME`. Both `files` and `file:FNAME` can
        be used, but each file must be specified only once.
    -   `transform-expected`: transformations to be applied to all
        expected output values (except `returncode`) before testing;
        the same options are supported as for `input: transform`
    -   `transform-actual`: transformations to be applied to all
        actual output values (except `returncode`) before testing;
        the same options are supported as for `input: transform`

    The expected values may have several different forms:

    1. a simple scalar value, in which case the actual value is
       compared for equality with it;
    2. a dict with `value` and possibly other optional items:
	   -   `value`: the expected value (obligatory): `str`, `int`,
           `None` or a `dict` of one item (see below)
	   -   `test`: the test name: one of the values shown below; if
		   omitted, defaults to `==`, that is, equality)
       -   `reflags`: regular expression flags for regular expression
           match tests
       -   `transform-expected`: transformations of the expected value
           (same options as for input transformations above)
       -   `transform-actual`: transformations of the actual value
           (same options as for input transformations above)
    3. a dict with test names (see below) as keys and expected values
       as values (the value may also be a list, in which case each
       item in the list is treated as a separate value to be tested);
    4. a list whose items may be any of the other: all tests must
       pass; or
	5. a dict with `transform-expected` or `transform-actual` or both
       (but with no `value`) for specifying file-specific
       transformations to be applied to all subsequent tests for the
       file after global but before value-specific transformations;
       this makes sense only when the expected value is a list with
       tests specified after the transformation item.

    Supported test names are the following, some with aliases
    (*actual* is the actual value, *expected* the expected value
    specified as the value, either directly or as the value of
    `value`):

    -   `==`, `equal`: *actual* equals *expected*
    -   `!=`, `not-equal`: *actual* is not equal to *expected*
    -   `<`, `less`: *actual* is less than *expected*
    -   `<=`, `less-equal`: *actual* is less than or equal to
        *expected*
    -   `>`, `greater`: *actual* is greater than *expected*
    -   `>=`, `greater-equal`: *actual* is greater than or equal to
        *expected*
    -   `in`: *actual* is contained in *expected*
    -   `not-in`: *actual* is not contained in *expected*
    -   `contains`: *actual* contains *expected*
    -   `not-contains`: *actual* does not contain *expected*
    -   `regex`, `matches`: *actual* matches the Python regular
        expression *expected* (using `re.search`)
    -   `not-regex`, `not-matches`: *actual* does not match the Python
        regular expression *expected* (using `re.search`)
    -   `python`: Python 3 code to test *actual*: the body of a
        function of one argument named `value` containing the actual
        value and returning `True` (when cast to `bool`) if the test
        passes. The Python regular expression module `re` is available
        for the code.
    -   `shell`: shell command line reading *actual* from standard
        input and returning true (0) if the test passes. The shell
        used is the default shell. The command line is executed in the
        temporary directory containing the input and output files and
        with the environment variables specified in `envvars` of
        `input`. The command should *not* change the input and output
        files.

    For the tests `regex` (`matches`) and `not-regex` (`not-matches`),
    a value for the `flags` parameter to the `re.search` function can
    be passed either via the value of `reflags` or appended to the
    test name, separated by whitespace. The value is as in Python,
    except that the names of the flag constants need not be prefixed
    by `re.`. For example, the test name may be `regex
    DOTALL|VERBOSE`, corresponding to `re.search(`*expected* `,
    `*actual* `, re.DOTALL|re.VERBOSE)`.

    For the tests `in` and `not-in`, the expected value may be either
    `str` or `list`: if `str`, the actual value should be contained in
    the expected one, and if `list`, the actual value should be one of
    the values in the list. Note that when using a `dict` with test
    names as keys, a `list` value should be enclosed in another
    `list`, so that it is not interpreted as multiple individual `str`
    values. A `list` value is transformed by transforming each item
    separately.

    A value may also be specified as a single-item `dict` with one of
    the following keys and value *val*, based on which the expected
    value (`str`) is generated as follows:

    -   `file`: the content of the file *val* in the temporary
        directory containing the input and output files (`None` if the
        file *val* does not exist).
    -   `python`: the value returned by the Python 3 function whose
        body is *val*; the function has no arguments.
    -   `shell`: the standard output produced by the shell command
        line *val*. The shell used is the default shell. The command
        line is executed in the temporary directory containing the
        input and output files and with the environment variables
        specified in `envvars` of `input`. The command should *not*
        change the input and output files.

    The value for a non-existent file is `None` in Python, and `null`,
    `~` or an empty value in YAML, so you can test that file
    `outfile.txt` does not exist as `file:outfile.txt: null` (YAML).

	Transforming actual values is useful in particular for removing
    such parts of the output that change on each run, such as
    timestamps.

	If both value-specific `transform-expected` or `transform-actual`
    and ones affecting all values are specified, the value-specific
    ones are applied after those affecting all values. File-specific
    transformations are applied after those affecting all files but
    before value-specific transformations. If file-specific
    transformations are specified in multiple batches for a file, the
    transformations of a batch are appended to the existing list of
    transformations, and all those transformations are applied to the
    tests after the batch.

-   `transform`: Grouped transformations: a list of `dict`s of
    transformations to be applied at the same time. These are used to
    generate multiple separate tests from the same base data with
    certain transformations. Each item in the list is used to generate
    a new test (or a set of tests) with the specified transformations
    applied. For example, adding a command line argument could be
    accompanied with a change to the output.

    The `dict`s in the list can contain the following keys:

    -   `name`: descriptive name for the transformation group
        (`str`)
    -   `input`: transformations to be added to input files and
        command line (`transform`)
    -   `output-expected`: transformations to be added to output
        (`transform-expected`)
    -   `output-actual`: transformations to be added to output
        (`transform-actual`)

    The value of `input`, `output-expected` and `output-actual` is a
    `dict` with keys corresponding to (transformable) items in the
    `input` and `output` `dict`s of a test (files, `cmdline`, `stdin`,
    `stdout`, `stderr`, `returncode`) and values corresponding to
    transformation `dict`s or lists of them, as for `transform` of
    `input` items and `transform-expected` and `transform-actual` of
    `output` items.

    Grouped transformations are applied to values after global,
    file-specific and test-specific ones.

    If untransformed tests should also be generated, the list must
    also include an empty `dict` `{}`.

-   `status`: The status of the test (optional). Tests should pass by
    default, but `status` can mark otherwise. Allowed values are:

	- `skip`: the test is skipped unconditionally;
	- `skipif:`*condition*: the test is skipped if *condition*
      evaluates to `True` (see [pytest
      documentation](https://docs.pytest.org/en/latest/historical-notes.html#string-conditions)
      for more information); or
    - `xfail`: the test is expected to fail.

	The values `skip` and `xfail` may optionally be followed by a
    colon and a reason (text) for the expected failure.

#### Default values

The sequence of test cases may also contain items specifying default
values for the tests that follow. Default value items contain the
single key `defaults`, whose value is a mapping, which may contain
keys `input`, `output` and `status`, with values as described above.
These values become default values for the test cases that follow; the
test cases can override the values individually. For example, the YAML
specification

    - defaults:
        input:
          cmdline: echo 'test\n'
          stdin: 'test\n'
        output:
          stdout: 'test\n'
    - name: Test
      input:
        cmdline: cat

is equivalent to

    - name: Test
      input:
        cmdline: cat
        stdin: 'test\n'
      output:
        stdout: 'test\n'

Similarly, a default values item overrides the values in a possible
previous default values. To clear the default values completely, use

    - defaults: {}

#### Reusable definitions

In a test specified in YAML, the sequence of test cases may contain
items defining reusable values with YAML anchors (`&`*anchor*) that
can be referenced to elsewhere via alias nodes (`*`*anchor*). These
items conventionally consist of a mapping with a single key `defs`,
whose value is sequence of items with YAML anchors. Alternatively, a
test case itself may contain `defs` with similar content.

For example:

    - defs:
      - &empty_output
          stdout: ''
          stderr: ''
          returncode: 0

This can be referenced in a test as follows:

    - name: Test
      input:
        cmdline: cat /dev/null
      output:
        *empty_output

This is equivalent to:

    - name: Test
      input:
        cmdline: cat /dev/null
      output:
        stdout: ''
        stderr: ''
        returncode: 0

**Note** that anchor names must be unique within a YAML file: even
though the YAML specification allows non-unique anchor names (an alias
node would refer to the nearest preceding anchor of the name), the
Python `yaml` module used in `scripttestlib` does not.

In Python code, reusable definitions need to be defined in a separate
variable (or separate variables) that can be referenced in multiple
places in the actual test cases. For example:

    _defs = {
        'empty_output': {
            'stdout': '',
            'stderr': '',
            'returncode': 0,
        },
    }
    testcases = [
        {
            'name': 'Test',
            'input': {
                'cmdline': 'cat /dev/null',
            },
            'output': _defs['empty_output'],
        },
    ]


### Test granularity

By default, each single output value generates a pytest test of its
own, with a single value assertion. Alternatively, you can group in
the same test all the value tests for an output item (such as
`stdout`) of a program run or all the tests for all output items of a
program run (test item). The granularity is specified with the custom
pytest command-line option `--scripttest-granularity`, whose value can
be `value` (default), `inputitem` or `programrun`.


### Generating a test case with `make-scripttest`

You can use the script `make-scripttest` in this directory to generate
a YAML representation of a test case based on a program run. The
output produced by the program run is considered as the expected
output.

The usage of `make-scripttest` is as follows:

`make-scripttest` `--name` *name* [ *options* ] *command* [ *args* ]
`>` *output.yaml*

The arguments are:

-   *name*: The name or description of the test.
-   *command*: The command (script or other program) to run
-   *args*: Arguments to *command*
-   *options*: One or more of the following options:
    -   `--input-files` *file* [ *file* ]: *command* uses the files
        *file* as input files; their content is recorded before the
        program run.
    -   `--output-files` *file* [ *file* ]: *command* outputs the
        files *file*: after the program run, their content is recorded
        as the expected output, in addition to standard output and
        standard error.
    -   `--environment-variables` *var* [ *var* ]: *command* uses the
        environment variables *var*: their content is recorded before
        the program run.
	-   `--use-cmdline`: output the full command as a single value
        (`cmdline`) instead of separate program (`prog`) and argument
        list (`args`)

`make-scripttest` writes to standard output a YAML description of the
program run. It can redirected to a file and used as a `scripttestlib`
test.
