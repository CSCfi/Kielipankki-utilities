
"""
test_strformatters.py

Pytest tests for libvrt.strformatters.
"""


import pytest

from libvrt.strformatters import PartialStringFormatter


class Namespace:

    """Empty class to be used as a namespace."""

    pass


class TestPartialStringFormatter:

    """Tests for PartialStringFormatter"""

    def test_all_keys_exist(self):
        """Test a case in which all format keys exist."""
        psf = PartialStringFormatter()
        ns = Namespace()
        ns.x = 4
        result = psf.format('{0}{1} a {a} b {b} c {c[0]} d {d[a]} e {ns.x}',
                            'x', 'y', a=1, b=2, c=[0], d={'a': 3}, ns=ns)
        assert result == 'xy a 1 b 2 c 0 d 3 e 4'

    def test_missing_arg(self):
        """Test a case with missing positional argument."""
        psf = PartialStringFormatter()
        result = psf.format('{0}{1} a {a} b {b}', 'x', a=1, b=2)
        assert result == 'x a 1 b 2'

    def test_missing_kwarg(self):
        """Test a case with missing keyword argument."""
        psf = PartialStringFormatter()
        result = psf.format('{0}{1} a {a} b {b}', 'x', 'y', a=1)
        assert result == 'xy a 1 b '

    def test_missing_list_item(self):
        """Test a case with a missing item in a list."""
        psf = PartialStringFormatter()
        result = psf.format('{a[0]} {a[1]}', a=[0])
        assert result == '0 '

    def test_missing_dict_key(self):
        """Test a case with a missing key in a dict."""
        psf = PartialStringFormatter()
        result = psf.format('{a[a]} {a[b]}', a={'a': 0})
        assert result == '0 '

    def test_missing_attr(self):
        """Test a case with a missing attribute."""
        psf = PartialStringFormatter()
        ns = Namespace()
        ns.a = 0
        result = psf.format('{ns.a} {ns.b}', ns=ns)
        assert result == '0 '

    def test_alternative_replacement_value(self):
        """Test a case with an alternative replacement value for missing."""
        psf = PartialStringFormatter('*')
        result = psf.format('{0}{1} a {a} b {b}', 'x', a=1)
        assert result == 'x* a 1 b *'
