
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
of dictionaries) in a Python module, or (2) a YAML file with the same
structure (a sequence of mappings), converted to the Python data
structure. You can also generate such a YAML file with the
`make-scripttest` script.


### The structure of a `scripttestlib` test

#### Test cases

A `scripttestlib` test contains the following information for a single
test case:

-   `name`: A name or description of the test (`str`)

-   `input_`: A dict containing input information for the test:
    -   `prog`: program (script) name (`str`). The program is searched
        in `$PATH` as usual, but for tests under this directory, the
        `vrt-tools` directory is added to `$PATH`, so the bare name of
        the script can be used when testing VRT Tools scripts.
    -   `args`: a list of command-line arguments, either a single
        string with arguments quoted as in shell, or as a list of
        unquoted strings (`str`)
    -   `cmdline`: complete command line (str), with arguments quoted
        as in shell (an alternative to `prog` and `args`)
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
    -   `stdin`: the content of standard input (`str`)
    -   `file:FNAME`: the content of file FNAME (`str`)

-   `output`: Expected output for the test:
    -   `returncode`: program return code (`int`)
    -   `stdout`: the content of standard output (`str`)
    -   `stderr`: the content of standard error (`str`)
    -   `file:FNAME`: the content of file FNAME (`str`)

    The expected values may have several different forms:

    1. simple scalar value, in which case the actual value is compared
       for equality with it;
    2. a dict of two items: `test` is the test name (one of the values
       shown below) and `value` the expected value (and possibly
       `opts` for options; see below);
    3. a dict with test names (see below) as keys and expected values
       as values (the value may also be a list, in which case each
       item in the list is treated as a separate value to be tested);
       or
    4. a list whose items may be any of the other: all tests must
       pass.

    Supported test names are the following (*actual* is the actual
    value, *expected* the expected value specified as the value,
    either directly or as the value of `value`):

    -   `==`: *actual* equals *expected*
    -   `!=`: *actual* is not equal to *expected*
    -   `<`: *actual* is less than *expected*
    -   `<=`: *actual* is less than or equal to *expected*
    -   `>`: *actual* is greater than *expected*
    -   `>=`: *actual* is greater than or equal to *expected*
    -   `in`: *actual* is contained in *expected*
    -   `not_in`: *actual* is not contained in *expected*
    -   `matches`: *actual* matches the Python regular expression
        *expected* (using `re.search`)
    -   `not_matches`: *actual* does not match the Python regular
        expression *expected* (using `re.search`)

    For the tests `matches` and `not_matches`, a value for the `flags`
    parameter to the `re.search` function can be passed either via the
    value of `opts` or appended to the test name, separated by
    whitespace. The value is as in Python, except that the names of
    the flag constants need not be prefixed by `re.`. For example, the
    test name may be `matches DOTALL|VERBOSE`, corresponding to
    `re.search(`*expected* `, `*actual* `, re.DOTALL|re.VERBOSE)`.

-   `status`: The status of the test (optional). Tests should be pass
    by default, but `status` can mark otherwise. Allowed values are:

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
