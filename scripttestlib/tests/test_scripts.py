# -*- mode: Python; -*-

"""
test_scripts.py

A pytest test module that collects the scripttestlib test cases in the
files scripttest_*.{py,yaml,yml} and scripttests/*.{py,yaml,yml} in
the directory of this module and runs them, with one parametrized test
function per test case file, so that the tests can be selected and
their output grouped by test case file (see
scripttestlib.pytest_grouped_output). The programs to be tested are
searched first in the parent directory of this module (the directory
of the script collection) and then in the directory of this module.

This module can be symlinked to the tests/ subdirectory of other
script collections at the top level of the repository. To run all the
test cases in a single test function, use
scripttestlib.collect_testcases instead; see its docstring.
"""


from scripttestlib import (
    collect_testcases_by_file, make_parametrized_test_functions)


testcases_by_file = collect_testcases_by_file()

test_funcs = make_parametrized_test_functions(testcases_by_file)

globals().update(test_funcs)
