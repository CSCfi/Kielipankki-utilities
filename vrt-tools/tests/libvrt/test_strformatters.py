
"""
test_strformatters.py

Pytest tests for libvrt.strformatters.
"""


import pytest

from libvrt.strformatters import (
    PartialFormatter,
    BytesFormatter,
    SubstitutingFormatter,
    SubstitutingBytesFormatter
)


class Namespace:

    """Empty class to be used as a namespace."""

    def __init__(self, **kwargs):
        """Set instance attributes from kwargs."""
        for key, val in kwargs.items():
            setattr(self, key, val)


def decode(val):
    """Decode UTF-8 bytes values in val recursively (list, dict, Namespace)."""
    if isinstance(val, bytes):
        return val.decode('UTF-8')
    elif isinstance(val, list):
        return [decode(item) for item in val]
    elif isinstance(val, dict):
        return dict((decode(k), decode(v)) for k, v in val.items())
    elif isinstance(val, Namespace):
        for attrname, attrval in val.__dict__.items():
            setattr(val, attrname, decode(attrval))
        return val
    else:
        return val


class TestPartialFormatter:

    """Tests for PartialFormatter"""

    def check_formatted(self, missing, expected, format, *args, **kwargs):
        """Assert that the result of PartialFormatter.format is expected.

        missing is passed to PartialFormatter; format, *args and
        **kwargs to PartialFormatter.format.
        """
        # The argument order with expected second might not be the
        # most natural, but we cannot have it after **kwargs
        pf = PartialFormatter(missing)
        result = pf.format(format, *args, **kwargs)
        assert result == expected

    def test_all_keys_exist(self):
        """Test a case in which all format keys exist."""
        self.check_formatted(
            '', 'xy a 1 b 2 c 0 d 3 e 4',
            '{0}{1} a {a} b {b} c {c[0]} d {d[a]} e {ns.x}',
            'x', 'y', a=1, b=2, c=[0], d={'a': 3}, ns=Namespace(x=4))

    def test_missing_arg(self):
        """Test a case with missing positional argument."""
        self.check_formatted('', 'x a 1 b 2',
                             '{0}{1} a {a} b {b}', 'x', a=1, b=2)

    def test_missing_kwarg(self):
        """Test a case with missing keyword argument."""
        self.check_formatted('', 'xy a 1 b ',
                             '{0}{1} a {a} b {b}', 'x', 'y', a=1)

    def test_missing_list_item(self):
        """Test a case with a missing item in a list."""
        self.check_formatted('', '0 ',
                             '{a[0]} {a[1]}', a=[0])

    def test_missing_dict_key(self):
        """Test a case with a missing key in a dict."""
        self.check_formatted('', '0 ',
                             '{a[a]} {a[b]}', a={'a': 0})

    def test_missing_attr(self):
        """Test a case with a missing attribute."""
        self.check_formatted('', '0 ',
                             '{ns.a} {ns.b}', ns=Namespace(a=0))

    def test_missing_args_none(self):
        """Test missing arguments, with None values."""
        self.check_formatted('', '|None||None||',
                             '|{0}|{1}|{a}|{b}|', None, a=None)

    def test_missing_args_with_formatspecs(self):
        """Test missing arguments, replacement fields with format specs."""
        self.check_formatted('', '|x |  | 1|  |',
                             '|{0:2}|{1:2}|{a:2}|{b:2}|', 'x', a=1)

    def test_missing_args_with_conversions(self):
        """Test missing arguments, replacement fields with conversions."""
        self.check_formatted('', '|x |  |1 |  |',
                             '|{0!s:2}|{1!s:2}|{a!s:2}|{b!s:2}|', 'x', a=1)

    def test_missing_args_with_conversions_none(self):
        """Test missing arguments, with conversions and None values."""
        self.check_formatted('', '|None|  |None|  |',
                             '|{0!s:2}|{1!s:2}|{a!s:2}|{b!s:2}|', None, a=None)

    def test_missing_args_with_conversions_repr_none(self):
        """Test missing arguments, with !r conversions and None values."""
        self.check_formatted('', '|None|\'\'|None|\'\'|',
                             '|{0!r:2}|{1!r:2}|{a!r:2}|{b!r:2}|', None, a=None)

    def test_alternative_replacement_value(self):
        """Test a case with an alternative replacement value for missing."""
        self.check_formatted('*', 'x* a 1 b *',
                             '{0}{1} a {a} b {b}', 'x', a=1)

    def test_alt_repl_value_with_formatspecs(self):
        """Test missing arguments, alternative replacement, format specs."""
        self.check_formatted('*', '|x |* | 1|* |',
                             '|{0:2}|{1:2}|{a:2}|{b:2}|', 'x', a=1)

    def test_alt_repl_value_with_repr_conversions(self):
        """Test missing arguments, alt replacement, format specs, !r."""
        self.check_formatted('*', '|\'x\'|\'*\'|1 |\'*\'|',
                             '|{0!r:2}|{1!r:2}|{a!r:2}|{b!r:2}|', 'x', a=1)

    def test_alt_repl_int_value_with_formatspecs(self):
        """Test missing arguments, int replacement, format specs."""
        self.check_formatted(0, '|x | 0| 1| 0|',
                             '|{0:2}|{1:2}|{a:2}|{b:2}|', 'x', a=1)

    def test_alt_repl_int_value_with_conversions(self):
        """Test missing arguments, int replacement, format specs, conversion."""
        self.check_formatted(0, '|x |0 |1 |0 |',
                             '|{0!s:2}|{1!s:2}|{a!s:2}|{b!s:2}|', 'x', a=1)

    def test_alt_repl_int_value_with_repr_conversions(self):
        """Test missing arguments, int replacement, format specs, !r."""
        self.check_formatted(0, '|\'x\'|0 |1 |0 |',
                             '|{0!r:2}|{1!r:2}|{a!r:2}|{b!r:2}|', 'x', a=1)

    def test_keep_replfields_missing_arg(self):
        """Test keeping replacement fields referring to missing arguments."""
        self.check_formatted(None, 'x{1} a 1 b {b}',
                             '{0}{1} a {a} b {b}', 'x', a=1)

    def test_keep_replfields_missing_args_all(self):
        """Test keeping all replacement fields (no arguments)."""
        fmt = '{0}{1} a {a} b {b}'
        self.check_formatted(None, fmt, fmt)

    def test_keep_replfields_missing_args_double_curlies(self):
        """Test keeping replacement fields, format with double curly brackets."""
        self.check_formatted(None, 'x{1} {0} a 1 b {b} {a}',
                             '{0}{1} {{0}} a {a} b {b} {{a}}', 'x', a=1)

    def test_keep_replfields_missing_list_item(self):
        """Test keeping a replacement field with a missing item in a list."""
        self.check_formatted(None, '0 ',
                             '{a[0]} {a[1]}', a=[0])

    def test_keep_replfields_missing_dict_key(self):
        """Test keeping a replacement field with a missing key in a dict."""
        self.check_formatted(None, '0 ',
                             '{a[a]} {a[b]}', a={'a': 0})

    def test_keep_replfields_missing_attr(self):
        """Test keeping a replacement field with a missing attribute."""
        self.check_formatted(None, '0 ',
                             '{ns.a} {ns.b}', ns=Namespace(a=0))


class TestBytesFormatter:

    """Tests for BytesFormatter"""

    def check_formatted(self, expected, format, *args, **kwargs):
        """Assert that the result of BytesFormatter.format is expected."""
        bf = BytesFormatter()
        result = bf.format(format, *args, **kwargs)
        assert result == expected

    def test_format_strings(self):
        """Test formatting strings with BytesFormatter."""
        ns = Namespace(a='2')
        self.check_formatted('|0|1|2|a|b|2|',
                             '|{0}|{1[0]}|{2.a}|{a}|{b[a]}|{ns.a}|',
                             0, [1, 2], ns, a='a', b={'a': 'b'}, ns=ns)

    def test_format_bytes_as_string(self):
        """Test formatting with converting bytes values to strings."""
        self.check_formatted('0a',
                             '{0}{a}', b'0', a=b'a')

    def test_format_bytes_list_item_as_string(self):
        """Test formatting with converting bytes list item values to strings."""
        self.check_formatted('0b',
                             '{0[0]}{a[1]}', [b'0', b'1'], a=[b'a', b'b'])

    def test_format_bytes_dict_value_as_string(self):
        """Test formatting with converting bytes dict values to strings."""
        self.check_formatted('0b',
                             '{0[a]}{a[b]}', {'a': b'0'}, a={'b': b'b'})

    def test_format_bytes_attr_value_as_string(self):
        """Test formatting with converting bytes attribute values to strings."""
        ns = Namespace(a=b'a', b=b'b')
        self.check_formatted('ab',
                             '{0.a}{ns.b}', ns, ns=ns)

    def test_format_bytes_dict_key_as_string(self):
        """Test formatting with converting bytes dict keys to strings."""
        self.check_formatted('0b',
                             '{0[a]}{a[b]}', {b'a': b'0'}, a={b'b': b'b'})


def substituting_format(format, *args, **kwargs):
    """Format with format, args and kwargs using SubstitutingFormatter.

    Decode bytes values in args and kwargs recursively to strings,
    assuming UTF-8, before passing to SubstitutingFormatter.
    """
    sf = SubstitutingFormatter()
    return sf.format(format,
                     *[decode(arg) for arg in args],
                     **dict((key, decode(val)) for key, val in kwargs.items()))


def substituting_bytes_format(format, *args, **kwargs):
    """Format with format, args and kwargs using SubstitutingBytesFormatter."""
    sf = SubstitutingBytesFormatter()
    return sf.format(format, *args, **kwargs)


@pytest.mark.parametrize('formatfn',
                         [substituting_format,
                          substituting_bytes_format])
class TestSubstitutingFormatters:

    """
    Tests for SubstitutingFormatter and SubstitutingBytesFormatter.

    The tests call the function passed as parameter formatfn, either
    substituting_format or substituting_bytes_format. The format argument
    values are bytes, which are converted to strings in
    substituting_format. In this way, the same code can be reused for
    testing both SubstitutingFormatter and SubstitutingBytesFormatter,
    which differ only in that SubstitutingBytesFormatter supports
    bytes values as format arguments.
    """

    def test_simple_substitution(self, formatfn):
        """Test simple substitution for a simple field."""
        result = formatfn('{0/a/b/} {a/b+/c/}',
                          b'aabbcc', a=b'aabbcc')
        assert result == 'bbbbcc aaccc'

    def test_simple_substitution_items(self, formatfn):
        """Test simple substitution for a indexed field and attribute."""
        result = formatfn('{0[1]/a/b/} {a[a]/b+/c/} {ns.a/c/x/}',
                          [b'', b'aabbcc'],
                          a={b'a': b'aabbcc'},
                          ns=Namespace(a=b'ccddee'))
        assert result == 'bbbbcc aaccc xxddee'

    def test_substitution_with_format_spec(self, formatfn):
        """Test substitution with a format specification."""
        result = formatfn('|{0/a/b/:8s}|{a/b+/c/:@^10s}|',
                          b'aabbcc', a=b'aabbcc')
        assert result == '|bbbbcc  |@@aaccc@@@|'

    def test_substitution_with_conversion(self, formatfn):
        """Test substitution with conversion."""
        result = formatfn('{0/a/b/!r} {a/b+/c/!s}',
                          b'aabbcc', a=b'aabbcc')
        assert result == '\'bbbbcc\' aaccc'

    def test_multiple_substitutions(self, formatfn):
        """Test multiple substitutions with different separators."""
        result = formatfn('{0 /a/b/, /b+/cc/ ; /c/dd/ /e/f//f/g/}',
                          b'aabbccddeeff')
        assert result == 'ddddddddddgggg'

    def test_substitution_groups(self, formatfn):
        """Test substitution with groups."""
        result = formatfn(
            r'{0/^([a-z])(.+?)(?P<x>[0-9]+)(.+)([a-z])$/\g<5>\g<4>\g<x>\3\2\1/}',
            b'abc123def')
        assert result == 'fde123123bca'

    def test_protect_slashes(self, formatfn):
        """Test substitutions with backslash-protected slashes."""
        result = formatfn(r'{0/\//\/\//} {1/(.)\/(.)/\2x\1}',
                          b'a//b', b'b/a')
        assert result == r'a////b axb'

    def test_handle_double_backslashes(self, formatfn):
        """Test substitutions with double backslashes."""
        # Important to test in particular at the end of a pattern or
        # substitution
        result = formatfn(r'{0/a\\b/b\\a/} {1/\\/\\\\/}',
                          br'aa\bb', br'b\a')
        assert result == r'ab\ab b\\a'
