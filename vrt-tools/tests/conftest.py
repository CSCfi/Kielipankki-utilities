#! /usr/bin/env python3


# Make pytest rewrite assertions in scripttestlib
# https://docs.pytest.org/en/latest/writing_plugins.html#assertion-rewriting

import pytest

pytest.register_assert_rewrite('scripttestlib')
