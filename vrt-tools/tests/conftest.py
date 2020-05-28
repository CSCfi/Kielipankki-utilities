# -*- mode: Python; -*-

# Make pytest rewrite assertions in scripttestlib
# https://docs.pytest.org/en/latest/writing_plugins.html#assertion-rewriting

import pytest

pytest.register_assert_rewrite('scripttestlib')

# Make tests find libraries in ../libvrt/ (and here in ../tests/).

import os.path
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__) + '/..'))
