
"""
test_iterutils.py

Pytest tests for libvrt.iterutils.
"""


import pytest

import libvrt.iterutils as iu


class TestFindDuplicates:

    """Tests for vrtlib.iterutils function find_duplicates."""

    @pytest.mark.parametrize(
        'input,expected', [
            ([], []),
            ([[]], []),
            ([[0, 1, 2]], []),
            ([[0, 1, 2, 1]], [1]),
            ([[0, 1, 2, 0, 1]], [0, 1]),
            ([[0, 1, 2], [0, 1]], [0, 1]),
            ([[0, 1, 2], [0, 1], [1, 2], [2, 3]], [0, 1, 2]),
            ([[0, 1, 2], {0: 3, 1: 4}.keys()], [0, 1]),
            ([['a', 'b'], ['b', 'c']], ['b']),
        ]
    )
    def test_find_duplicates(self, input, expected):
        """Test find_duplicates() with various inputs."""
        assert iu.find_duplicates(*input) == expected
