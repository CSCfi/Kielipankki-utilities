# -*- mode: Python; -*-


import pytest


# Make pytest rewrite assertions in scripttestlib
# https://docs.pytest.org/en/latest/writing_plugins.html#assertion-rewriting

pytest.register_assert_rewrite('tests.scripttestlib')


def pytest_addoption(parser):
    """Add custom option --scripttest-granularity to pytest."""
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


# The value of --scripttest-granularity, set in pytest_configure below
option_scripttest_granularity = None


def pytest_configure(config):
    """Make the value of --scripttest-granularity accessible.

    Make the value of --scripttest-granularity accessible as
    tests.conftest.option_scripttest_granularity.

    This works around the removal of the global pytest.config in
    pytest 5.0. Apparently the recommended approach would be to create
    a fixture for accessing the option via the request fixture:
    https://docs.pytest.org/en/stable/example/simple.html#request-example
    However, we need the value in scripttestlib, not directly in test
    functions, so it would not be possible to use a fixture.
    """
    global option_scripttest_granularity
    option_scripttest_granularity = config.option.scripttest_granularity


# Make tests find libraries in ../libvrt/ (and here in ../tests/).

import os.path
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__) + '/..'))
