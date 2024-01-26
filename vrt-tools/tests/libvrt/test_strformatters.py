
"""
test_strformatters.py

Pytest tests for libvrt.strformatters.
"""


import pytest

from libvrt.strformatters import PartialStringFormatter, BytesFormatter


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

    def test_missing_args_none(self):
        """Test missing arguments, with None values."""
        psf = PartialStringFormatter()
        result = psf.format('|{0}|{1}|{a}|{b}|', None, a=None)
        assert result == '|None||None||'

    def test_missing_args_with_formatspecs(self):
        """Test missing arguments, replacement fields with format specs."""
        psf = PartialStringFormatter()
        result = psf.format('|{0:2}|{1:2}|{a:2}|{b:2}|', 'x', a=1)
        assert result == '|x |  | 1|  |'

    def test_missing_args_with_conversions(self):
        """Test missing arguments, replacement fields with conversions."""
        psf = PartialStringFormatter()
        result = psf.format('|{0!s:2}|{1!s:2}|{a!s:2}|{b!s:2}|', 'x', a=1)
        assert result == '|x |  |1 |  |'

    def test_missing_args_with_conversions_none(self):
        """Test missing arguments, with conversions and None values."""
        psf = PartialStringFormatter()
        result = psf.format('|{0!s:2}|{1!s:2}|{a!s:2}|{b!s:2}|', None, a=None)
        assert result == '|None|  |None|  |'

    def test_missing_args_with_conversions_repr_none(self):
        """Test missing arguments, with !r conversions and None values."""
        psf = PartialStringFormatter()
        result = psf.format('|{0!r:2}|{1!r:2}|{a!r:2}|{b!r:2}|', None, a=None)
        assert result == '|None|\'\'|None|\'\'|'

    def test_alternative_replacement_value(self):
        """Test a case with an alternative replacement value for missing."""
        psf = PartialStringFormatter('*')
        result = psf.format('{0}{1} a {a} b {b}', 'x', a=1)
        assert result == 'x* a 1 b *'

    def test_alt_repl_value_with_formatspecs(self):
        """Test missing arguments, alternative replacement, format specs."""
        psf = PartialStringFormatter('*')
        result = psf.format('|{0:2}|{1:2}|{a:2}|{b:2}|', 'x', a=1)
        assert result == '|x |* | 1|* |'

    def test_alt_repl_value_with_repr_conversions(self):
        """Test missing arguments, alt replacement, format specs, !r."""
        psf = PartialStringFormatter('*')
        result = psf.format('|{0!r:2}|{1!r:2}|{a!r:2}|{b!r:2}|', 'x', a=1)
        assert result == '|\'x\'|\'*\'|1 |\'*\'|'

    def test_alt_repl_int_value_with_formatspecs(self):
        """Test missing arguments, int replacement, format specs."""
        psf = PartialStringFormatter(0)
        result = psf.format('|{0:2}|{1:2}|{a:2}|{b:2}|', 'x', a=1)
        assert result == '|x | 0| 1| 0|'

    def test_alt_repl_int_value_with_conversions(self):
        """Test missing arguments, int replacement, format specs, conversion."""
        psf = PartialStringFormatter(0)
        result = psf.format('|{0!s:2}|{1!s:2}|{a!s:2}|{b!s:2}|', 'x', a=1)
        assert result == '|x |0 |1 |0 |'

    def test_alt_repl_int_value_with_repr_conversions(self):
        """Test missing arguments, int replacement, format specs, !r."""
        psf = PartialStringFormatter(0)
        result = psf.format('|{0!r:2}|{1!r:2}|{a!r:2}|{b!r:2}|', 'x', a=1)
        assert result == '|\'x\'|0 |1 |0 |'

    def test_keep_replfields_missing_arg(self):
        """Test keeping replacement fields referring to missing arguments."""
        psf = PartialStringFormatter(None)
        result = psf.format('{0}{1} a {a} b {b}', 'x', a=1)
        assert result == 'x{1} a 1 b {b}'

    def test_keep_replfields_missing_args_all(self):
        """Test keeping all replacement fields (no arguments)."""
        psf = PartialStringFormatter(None)
        fmt = '{0}{1} a {a} b {b}'
        result = psf.format(fmt)
        assert result == fmt

    def test_keep_replfields_missing_args_double_curlies(self):
        """Test keeping replacement fields, format with double curly brackets."""
        psf = PartialStringFormatter(None)
        result = psf.format('{0}{1} {{0}} a {a} b {b} {{a}}', 'x', a=1)
        assert result == 'x{1} {0} a 1 b {b} {a}'

    def test_keep_replfields_missing_list_item(self):
        """Test keeping a replacement field with a missing item in a list."""
        psf = PartialStringFormatter(None)
        result = psf.format('{a[0]} {a[1]}', a=[0])
        assert result == '0 '

    def test_keep_replfields_missing_dict_key(self):
        """Test keeping a replacement field with a missing key in a dict."""
        psf = PartialStringFormatter(None)
        result = psf.format('{a[a]} {a[b]}', a={'a': 0})
        assert result == '0 '

    def test_keep_replfields_missing_attr(self):
        """Test keeping a replacement field with a missing attribute."""
        psf = PartialStringFormatter(None)
        ns = Namespace()
        ns.a = 0
        result = psf.format('{ns.a} {ns.b}', ns=ns)
        assert result == '0 '


class TestBytesFormatter:

    """Tests for BytesFormatter"""

    def test_format_strings(self):
        """Test formatting strings with BytesFormatter."""
        bf = BytesFormatter()
        ns = Namespace()
        ns.a = '2'
        result = bf.format('|{0}|{1[0]}|{2.a}|{a}|{b[a]}|{ns.a}|',
                           0, [1, 2], ns, a='a', b={'a': 'b'}, ns=ns)
        assert result == '|0|1|2|a|b|2|'

    def test_format_bytes_as_string(self):
        """Test formatting with converting bytes values to strings."""
        bf = BytesFormatter()
        result = bf.format('{0}{a}', b'0', a=b'a')
        assert result == '0a'

    def test_format_bytes_list_item_as_string(self):
        """Test formatting with converting bytes list item values to strings."""
        bf = BytesFormatter()
        result = bf.format('{0[0]}{a[1]}', [b'0', b'1'], a=[b'a', b'b'])
        assert result == '0b'

    def test_format_bytes_dict_value_as_string(self):
        """Test formatting with converting bytes dict values to strings."""
        bf = BytesFormatter()
        result = bf.format('{0[a]}{a[b]}', {'a': b'0'}, a={'b': b'b'})
        assert result == '0b'

    def test_format_bytes_attr_value_as_string(self):
        """Test formatting with converting bytes attribute values to strings."""
        bf = BytesFormatter()
        ns = Namespace()
        ns.a = b'a'
        ns.b = b'b'
        result = bf.format('{0.a}{ns.b}', ns, ns=ns)
        assert result == 'ab'

    def test_format_bytes_dict_key_as_string(self):
        """Test formatting with converting bytes dict keys to strings."""
        bf = BytesFormatter()
        result = bf.format('{0[a]}{a[b]}', {b'a': b'0'}, a={b'b': b'b'})
        assert result == '0b'
