
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
    modules or [YAML](https://yaml.org/) files in the subdirectory
    `scripttests` or with the file name prefix `scripttest_`. This
    facility is based on pytest, using the Python module
    [`scripttestlib`](../../scripttestlib/README.md) and the pytest
    test module
    [`test_scripts.py`](../../scripttestlib/tests/test_scripts.py).
    Please see [`scripttestlib`](../../scripttestlib/README.md) for
    more information.
