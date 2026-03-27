
"""
Package scripttestlib

The scripttestlib library for processing tests of complete scripts,
for running with pytest.

See ../README.md for more information on the scripttestlib script
testing module.
"""


import pytest


# Make pytest rewrite assertions in scripttestlib; this needs to be
# before importing _scripttestlib, and having _scripttestlib as a
# module in a package makes it possible to import the package and
# register rewriting here:
# https://docs.pytest.org/en/latest/writing_plugins.html#assertion-rewriting
pytest.register_assert_rewrite('scripttestlib._scripttestlib')


# Make all public functions in _scripttestlib visible here
from ._scripttestlib import (
    pytest_addoption_scripttestlib,
    pytest_configure_scripttestlib,
    set_scripttest_granularity,
    make_param_id,
    collect_testcases,
    collect_testcases_by_file,
    make_parametrized_test_functions,
    expand_testcases,
    dict_deep_update,
    check_program_run,
)
