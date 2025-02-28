
"""
test_datatypes.py

Pytest tests for `libvrt.datatypes`.
"""


import pytest

import libvrt.datatypes as dt


@pytest.fixture()
def sbd():
    """Yield a simple StrBytesDict instance."""
    yield dt.StrBytesDict([(b'a', b'c'), (b'd', b'e')])


class TestStrBytesDict:

    """Tests for `StrBytesDict`."""

    def test_getitem_bytes(self, sbd):
        """Test `d[key]` with a `bytes` key (and value)."""
        assert sbd[b'a'] == b'c'
        assert sbd.get(b'a') == b'c'

    def test_getitem_bytes_nonexistent(self, sbd):
        """Test `d[key]` with a non-existent `bytes` key."""
        with pytest.raises(KeyError, match='^b\'c\'$'):
            x = sbd[b'c']
        assert sbd.get(b'c') == None

    def test_getitem_str_bytes(self, sbd):
        """Test `d[key]` with a `str` key with corresponding `bytes` key."""
        assert sbd['a'] == 'c'
        assert 'a' in sbd

    def test_get_str_bytes(self, sbd):
        """Test `d.get(key)` with a `str` key with corresponding `bytes` key."""
        assert sbd.get('a') == 'c'
        assert 'a' in sbd

    def test_getitem_str_nonexistent(self, sbd):
        """Test `d[key]` with a `str` key without corresponding `bytes` key."""
        with pytest.raises(KeyError, match='^\'c\'$'):
            x = sbd['c']
        assert sbd.get('c') == None
        assert 'c' not in sbd

    def test_convert_to_bytes_getitem(self, sbd):
        """Test `.convert_to_bytes` with `str` key added by accessing it."""
        x = sbd['a']
        sbd['a'] += '1'
        assert 'a' in sbd
        assert sbd['a'] == 'c1'
        assert sbd[b'a'] == b'c'
        sbd.convert_to_bytes()
        # Key 'a' has been removed, but the value of b'a' has been
        # updated
        assert 'a' not in sbd
        assert b'a' in sbd
        assert sbd[b'a'] == b'c1'

    def test_convert_to_bytes_setitem(self, sbd):
        """Test `.convert_to_bytes` with `str` key added by assigning to it."""
        sbd['x'] = 'y'
        assert 'x' in sbd
        assert b'x' not in sbd
        assert sbd['x'] == 'y'
        sbd.convert_to_bytes()
        # Key 'x' has been removed, but the value of b'x' has been
        # added
        assert 'x' not in sbd
        assert b'x' in sbd
        assert sbd[b'x'] == b'y'
