# -*- mode: Python; -*-

"""
conftest.py

pytest conftest.py for the scripttestlib library.

This conftest.py can also be symlinked to the tests/ subdirectory of
other top-level script collections if they only use scripttestlib and
pytest tests.
"""


import os.path
import sys

# Make tests find scripttestlib and local library modules under
# _parent_dir, assuming that this file is copied or symlinked under
# _parent_dir/tests and that _parent_dir is at the same level as
# scripttestlib (top-level directory of the repository).
_parent_dir = os.path.abspath(os.path.dirname(__file__) + '/..')
sys.path.extend([_parent_dir + '/../scripttestlib', _parent_dir])

import scripttestlib
import scripttestlib.pytest_grouped_output


def pytest_addoption(parser):
    """Add scripttestlib custom option(s)."""
    scripttestlib.pytest_addoption_scripttestlib(parser)
    # Add grouped output plugin options
    scripttestlib.pytest_grouped_output.pytest_addoption(parser)


def pytest_configure(config):
    """Pass the value of scripttestlib custom option(s) and configure plugins."""
    scripttestlib.pytest_configure_scripttestlib(config)
    # Register the grouped output plugin for test_scripts_grouped.py
    scripttestlib.pytest_grouped_output.pytest_configure(config)
