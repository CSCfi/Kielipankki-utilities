#! /usr/bin/env python3


"""
test_scripts.py

A pytest test that collects and runs testcases specified in scripttest_*.py
and scripttest_*.yaml files, organizing them by source file so that the
pytest output groups tests by their source YAML/Python file.

This module provides better organization when there are many test files.
Each YAML/Python file gets its own test function and is displayed separately
in pytest output, making it easier to identify which test group is running
and to filter tests by source file.

This is the recommended approach for using scripttestlib. For documentation
on the older flat approach, see the git history.
"""


from scripttestlib import (
    collect_testcases_by_file, make_parametrized_test_functions)


# Collect testcases grouped by file
testcases_by_file = collect_testcases_by_file()

# Generate parametrized test functions, one per file
test_funcs = make_parametrized_test_functions(testcases_by_file)

# Register all test functions in this module's globals
globals().update(test_funcs)
