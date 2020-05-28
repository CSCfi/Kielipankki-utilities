#! /usr/bin/env python3


"""
test_scripts.py

A pytest test that collects and runs all the testcases specified in
scripttest_*.py and scripttest_*.yaml files in this directory, using
the scripttestlib module.
"""


import os.path

import pytest

from tests.scripttestlib import collect_testcases, check_program_run


_filedir = os.path.dirname(os.path.abspath(__file__))

# Collect testcases to a list of triples (descr, input, expected) to be used
# with @pytest.mark.parametrize below.
testcases = collect_testcases(
    'scripttest_*.py', 'scripttest_*.yaml', 'scripttest_*.yml',
    basedir=_filedir)


# Run all the test cases

@pytest.mark.parametrize("name, input, expected", testcases)
def test_scripts(name, input, expected, tmpdir):
    check_program_run(
        name, input, expected, str(tmpdir),
        progpath='{filedir}/..:{filedir}:{{PATH}}'.format(filedir=_filedir))
