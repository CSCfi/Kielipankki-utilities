# -*- mode: Python; -*-


import pytest

# Make pytest rewrite assertions in scripttestlib; this needs to be before
# importing scripttestlib:
# https://docs.pytest.org/en/latest/writing_plugins.html#assertion-rewriting
pytest.register_assert_rewrite('tests.scripttestlib')

import tests.scripttestlib as scripttestlib


def pytest_addoption(parser):
    """Add custom option --scripttest-granularity to pytest."""
    scripttestlib.add_pytest_option_scripttest_granularity(parser)


def pytest_configure(config):
    """Pass the value of --scripttest-granularity to scripttestlib."""
    scripttestlib.set_scripttest_granularity(
        config.option.scripttest_granularity)


# Make tests find libraries in ../libvrt/ (and here in ../tests/).

import os.path
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__) + '/..'))
